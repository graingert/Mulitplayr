import webapp2
import inspect

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

class BaseGameState(polymodel.PolyModel):
    current_player = db.UserProperty()
    last_sequence_number = db.IntegerProperty(required=True, default=-1)

    def get_actions_since(self,seq_num):
        return self.basegameaction_set.filter('sequence_number >', seq_num)

    def add_action(self,action):
        action.game_state = self
        self.last_sequence_number += 1
        action.sequence_number = self.last_sequence_number
        action.player = self.current_player

    def end_turn(self):
        players = self.parent().players
        current_index = players.index(self.current_player)
        next_index = current_index + 1
        if next_index >= len(players):
            next_index = 0
        self.current_player = players[next_index]

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = dict()
        target['current_player'] = self.current_player
        target['last_sequence_number'] = self.last_sequence_number

        return target

class BaseGameAction(polymodel.PolyModel):
    game_state = db.ReferenceProperty(BaseGameState)
    sequence_number = db.IntegerProperty()
    player = db.UserProperty()

    def get_info_dict(self, target=None):
        """ Fill info about action into a dict. """
        if target is None:
            target = dict()
        target['player'] = self.player.nickname()
        target['sequence_number'] = self.sequence_number

        return target


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
