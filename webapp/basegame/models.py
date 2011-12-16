import webapp2

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

class BaseGameState(polymodel.PolyModel):
    current_participant = db.UserProperty()
    last_sequence_number = db.IntegerProperty(required=True, default=0)

    def get_actions_since(self,seq_num):
        return self.basegameaction_set.filter('sequence_number >', seq_num)

    def add_action(self,action):
        action.game_state = self
        action.sequence_number = last_sequence_number
        last_sequence_number += 1
        action.participant = current_participant
        action.put()
        self.put()

class BaseGameAction(polymodel.PolyModel):
    game_state = db.ReferenceProperty(BaseGameState)
    sequence_number = db.IntegerProperty(required=True)
    participant = db.UserProperty()

class BaseGameInstance(polymodel.PolyModel):
    state = db.StringProperty(required=True, choices=set(["open", "playing", "finished"]))
    created = db.DateProperty(required=True)
    participants = db.ListProperty(users.User)
    current_state = db.ReferenceProperty(BaseGameState)
    max_participants = 2

    def start_game(self):
        # Check if the game can be started
        if self.state != "open":
            return False

        # Set the current to the initial state
        new_state = self.new_initial_state()
        new_state.current_participant = self.participants[0]
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
        if user in self.participants:
            return False

        self.participants.append(user)
        self.put()
        return True

    def prepare_info_context(self, context):
        context['state'] = self.state
        context['participants'] = self.participants
        return context
