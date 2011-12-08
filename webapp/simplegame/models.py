import webapp2

from google.appengine.ext import db

from basegame.models import BaseGameInstance, BaseGameState

class SimpleGameState(BaseGameState):
    current_number = db.IntegerProperty()

class SimpleGameInstance(BaseGameInstance):
    current_state = db.ReferenceProperty(SimpleGameState)
    def start_game(self):
        if self.state != "open":
            return False
        current_state = SimpleGameState()
        current_state.current_number = 1
        current_state.next_participant = self.participants[0]
        current_state.put()

        self.current_state = current_state
        self.state = "playing"
        self.put()
        return current_state
