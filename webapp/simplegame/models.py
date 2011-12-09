import webapp2
import inspect

from google.appengine.ext import db

from basegame.models import BaseGameInstance, BaseGameState

class SimpleGameState(BaseGameState):
    current_number = db.IntegerProperty()

class SimpleGameInstance(BaseGameInstance):
    current_state = db.ReferenceProperty(SimpleGameState)
    def new_initial_state(self):
        current_state = SimpleGameState()
        current_state.current_number = 1
        current_state.next_participant = self.participants[0]
        current_state.put()
        return current_state
