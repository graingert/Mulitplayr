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

    def setup(self):
        """ Setup the initial state. """
        self.check_state('init')
        
        for i in range(9):
            self.grid.append(0)

        self.state = 'playing'

    def place_action(self, position):
        """ Place Marker. """
        self.check_state('playing')

        user = users.get_current_user()
        if user != self.current_player:
            raise NotTurnException()

        # Construct action
        action = OxPlaceAction(parent = self)
        action.position = position
        self.add_action(action)

        # New state
        self.grid[position] = 1
        # TODO Win Transition
        self.end_turn()

        return action

class OxInstance(BaseGameInstance):
    info_redirect = "oxgameinfo"
    play_redirect = "oxgameplay"

    def new_initial_state(self):
        current_state = OxState(parent=self)
        current_state.setup()
        return current_state

class OxPlaceAction(BaseGameAction):
    position = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        
        target['type'] = 'place'

        return target
