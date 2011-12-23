import webapp2
import inspect

from google.appengine.ext import db

from basegame.models import BaseGameInstance, BaseGameState

class SimpleGameState(BaseGameState):
    current_number = db.IntegerProperty()

class SimpleGameInstance(BaseGameInstance):
    info_redirect = "simplegameinfo"
    play_redirect = "simplegameplay"

    def new_initial_state(self):
        current_state = SimpleGameState()
        current_state.current_number = 1
        return current_state

class SimpleGameAction(BaseGameInstance):
    pass
