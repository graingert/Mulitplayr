import webapp2

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

class BaseGameInstance(polymodel.PolyModel):
    state = db.StringProperty(required=True, choices=set(["open", "playing", "finished"]))
    created = db.DateProperty(required=True)
    participants = db.ListProperty(users.User)

    def start_game(self):
        # Check if the game can be started
        if self.state != "open":
            return False

        # Set the current to the initial state
        self.current_state = self.new_initial_state()
        self.state = "playing"
        self.put()
        return self.current_state

class BaseGameState(db.Model):
    next_participant = db.UserProperty()
