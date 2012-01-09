import webapp2
import random

from google.appengine.ext import db
from google.appengine.api import users

from basegame.models import *

class InvalidMoveException(Exception):
    pass

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

        self.is_current_player()

        # Construct action
        action = OxPlaceAction(parent = self)
        action.position = position
        self.add_action(action)

        # New state
        if self.grid[position] != -1:
            raise InvalidMoveException()
        self.grid[position] = self.current_player_index
        win_cons = [[1,1,1,0,0,0,0,0,0],
                    [0,0,0,1,1,1,0,0,0],
                    [0,0,0,0,0,0,1,1,1],
                    [1,0,0,1,0,0,1,0,0],
                    [0,1,0,0,1,0,0,1,0],
                    [0,0,1,0,0,1,0,0,1],
                    [1,0,0,0,1,0,0,0,1],
                    [0,0,1,0,1,0,1,0,0]]
        for check_var in [0,1]:
            for cond in win_cons:
                match = 0
                for i,v in enumerate(cond):
                    if self.grid[i] == check_var and v:
                        match+=1
                if match == 3:
                    self.state = 'finished'
                    action.new_state = 'finished'
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
    game_name = "ox"
    human_name = 'Naughts and Crosses'
    description = """
9 squares, 2 players and one winner (sometimes). Pit yourself against
friends and family in this onine reimagining of the classic classroom
game
    """
    min_players = 2

    info_redirect = "oxgameinfo"
    play_redirect = "oxgameplay"

    game_player_type = OxPlayer
    game_state_type = OxState


class OxPlaceAction(BaseGameAction):
    position = db.IntegerProperty()
    action_type = "place"

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)

        return target
