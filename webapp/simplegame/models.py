import webapp2
import random

from google.appengine.ext import db
from google.appengine.api import users

from basegame.models import *

class SimpleGameState(BaseGameState):
    current_number = db.IntegerProperty()
    correct_number = db.IntegerProperty()
    possible_states = BaseGameState.possible_states | set(['guessing'])
    # State required here for possible_states support
    state = db.StringProperty(choices=possible_states, default='init')

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = dict()
        BaseGameState.get_info_dict(self, target)
        
        target['current_number'] = self.current_number

        return target

    def setup(self):
        """ Setup the initial state. """
        self.check_state('init')

        self.current_number = -1
        self.correct_number = random.randrange(1,101)

        self.state = 'guessing'

    def guess_action(self, guessed_number):
        """ Make the guess of a number """
        self.check_state('guessing')

        user = users.get_current_user()
        if user != self.get_current_player():
            raise NotTurnException()

        # Construct action
        action = SimpleGameAction(parent = self)
        action.guessed_number = guessed_number
        self.add_action(action)

        # New state
        self.current_number = guessed_number
        if guessed_number == self.correct_number:
            action.new_state = 'finished'
            self.state = 'finished'
        else:
            # End players turn
            self.end_turn()

        return action


class SimpleGamePlayer(BaseGamePlayer):
    def get_info_dict(self, target=None):
        """ Fill info about player into a dict. """
        if target is None:
            target = dict()
        BaseGamePlayer.get_info_dict(self, target)

        return target


class SimpleGameInstance(BaseGameInstance):
    info_redirect = "simplegameinfo"
    play_redirect = "simplegameplay"

    game_player_type = SimpleGamePlayer
    game_state_type = SimpleGameState


class SimpleGameAction(BaseGameAction):
    guessed_number = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        
        target['type'] = 'guess'
        target['guessed_number'] = self.guessed_number
        if self.guessed_number < self.parent().correct_number:
            target['dir'] = "Higher"
        if self.guessed_number > self.parent().correct_number:
            target['dir'] = "Lower"

        return target
