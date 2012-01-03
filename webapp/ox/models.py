import webapp2
import random

from google.appengine.ext import db
from google.appengine.api import users

from basegame.models import *

class OxState(BaseGameState):
    grid = db.ListProperty(int)
    possible_states = BaseGameState.possible_states | set(['playing'])
    # State required here for possible_states support
    state = db.StringProperty(choices=possible_states, default='init')

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = dict()
        BaseGameState.get_info_dict(self, target)
        
        target['grid'] = self.grid

        return target

    def setup(self,players):
        """ Setup the initial state. """
        self.check_state('init')

        players[0].player_symbol = 'O'
        players[1].player_symbol = 'X'
        
        for i in range(9):
            self.grid.append(-1)

        self.state = 'playing'

    def place_action(self, position):
        """ Place Marker. """
        self.check_state('playing')

        user = users.get_current_user()
        if user != self.get_current_player():
            raise NotTurnException()

        # Construct action
        action = OxPlaceAction(parent = self)
        action.position = position
        self.add_action(action)

        # New state
        self.grid[position] = self.current_player_index
        # TODO Win Transition
        self.end_turn()

        return action


class OxPlayer(BaseGamePlayer):
    player_symbol = db.StringProperty(choices=set(['O','X']))

    def get_info_dict(self, target=None):
        """ Fill info about player into a dict. """
        if target is None:
            target = dict()
        BaseGamePlayer.get_info_dict(self, target)

        target['player_symbol'] = self.player_symbol

        return target


class OxInstance(BaseGameInstance):
    info_redirect = "oxgameinfo"
    play_redirect = "oxgameplay"

    game_player_type = OxPlayer
    game_state_type = OxState


class OxPlaceAction(BaseGameAction):
    position = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        
        target['type'] = 'place'

        return target
