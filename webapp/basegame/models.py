import webapp2

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

class BaseGameState(polymodel.PolyModel):
    current_player = db.UserProperty()
    last_sequence_number = db.IntegerProperty(required=True, default=0)

    def get_actions_since(self,seq_num):
        return self.basegameaction_set.filter('sequence_number >', seq_num)

    def add_action(self,action):
        action.game_state = self
        action.sequence_number = self.last_sequence_number
        self.last_sequence_number += 1
        action.player = self.current_player
        action.put()
        self.put()

class BaseGameAction(polymodel.PolyModel):
    game_state = db.ReferenceProperty(BaseGameState)
    sequence_number = db.IntegerProperty()
    player = db.UserProperty()

class BaseGameInstance(polymodel.PolyModel):
    state = db.StringProperty(required=True, choices=set(["open", "playing", "finished"]))
    created = db.DateProperty(required=True)
    players = db.ListProperty(users.User)
    current_state = db.ReferenceProperty(BaseGameState)
    max_players = 2

    def start_game(self):
        # Check if the game can be started
        if self.state != "open":
            return False

        # Set the current to the initial state
        new_state = self.new_initial_state()
        new_state.current_player = self.players[0]
        new_state.put()
        self.current_state = new_state
        self.state = "playing"
        self.put()
        return self.current_state

    def add_user(self, user):
        # Check if the game can be joined
        if self.state != "open":
            return False
        
        # Check if the user is already joined
        if user in self.players:
            return False

        self.players.append(user)
        self.put()
        return True
