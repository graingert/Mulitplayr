import webapp2
import random

from google.appengine.ext import db
from google.appengine.api import users

from basegame.models import BaseGameInstance, BaseGameState, BaseGameAction
from basegame.handlers import NotTurnException

class SimpleGameState(BaseGameState):
    current_number = db.IntegerProperty()
    correct_number = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = dict()
        BaseGameState.get_info_dict(self, target)
        
        target['current_number'] = self.current_number

        return target

    def guess_action(self, guessed_number):
        user = users.get_current_user()
        if user != self.current_player:
            raise NotTurnException()

        # Construct action
        action = SimpleGameAction(parent = self)
        action.guessed_number = guessed_number
        self.add_action(action)

        # New state
        self.current_number = guessed_number
        if guessed_number == self.correct_number:
            pass # TODO Win!
        else:
            # End players turn
            self.end_turn()

        return action

class SimpleGameInstance(BaseGameInstance):
    info_redirect = "simplegameinfo"
    play_redirect = "simplegameplay"

    def new_initial_state(self):
        current_state = SimpleGameState(parent=self)
        current_state.current_number = -1
        current_state.correct_number = random.randrange(1,101)
        return current_state

class SimpleGameAction(BaseGameAction):
    guessed_number = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        
        target['guessed_number'] = self.guessed_number
        if self.guessed_number < self.parent().correct_number:
            target['dir'] = "Higher"
        if self.guessed_number > self.parent().correct_number:
            target['dir'] = "Lower"

        return target
