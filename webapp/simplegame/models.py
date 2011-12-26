import webapp2
import random

from google.appengine.ext import db

from basegame.models import BaseGameInstance, BaseGameState, BaseGameAction

class SimpleGameState(BaseGameState):
    current_number = db.IntegerProperty()
    correct_number = db.IntegerProperty()

    def get_info_dict(self, target=dict()):
        """ Fill info about state into a dict. """
        BaseGameState.get_info_dict(self, target)
        
        target['current_number'] = self.current_number

        return target

class SimpleGameInstance(BaseGameInstance):
    info_redirect = "simplegameinfo"
    play_redirect = "simplegameplay"

    def new_initial_state(self):
        current_state = SimpleGameState(parent=self)
        current_state.current_number = 1
        current_state.correct_number = random.randrange(1,101)
        return current_state

class SimpleGameAction(BaseGameAction):
    guessed_number = db.IntegerProperty()
