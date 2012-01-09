import webapp2

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

from profile.models import *

class NotTurnException(Exception):
    pass

class InvalidStateException(Exception):
    pass

class InvalidActionParametersException(Exception):
    pass

class BaseGameState(polymodel.PolyModel):
    current_player_index = db.IntegerProperty(default=0)
    total_players = db.IntegerProperty()
    last_sequence_number = db.IntegerProperty(required=True, default=-1)
    possible_states = set(['init', 'finished'])

    def __init__(self, parent=None, key_name=None, **kwds):
        polymodel.PolyModel.__init__(self, parent, key_name, **kwds)

    def get_actions_since(self,seq_num):
        """ Get the actions since a given sequence number """
        return self.basegameaction_set.filter('sequence_number >', seq_num)

    def add_action(self,action):
        """ Add info to action and increment sequence number. """
        action.game_state = self
        self.last_sequence_number += 1
        action.sequence_number = self.last_sequence_number
        action.player_index = self.current_player_index

    def check_state(self, valid_state):
        """ Check that the game is in a given state. """
        if self.state != valid_state:
            raise InvalidStateException

    def check_states(self, valid_states):
        """ Check that the game is in one of the given states. """
        if self.state not in valid_states:
            raise InvalidStateException

    def end_turn(self):
        """ Move to the next player. """
        players = self.basegameplayer_set
        original_index = self.current_player_index
        found_next_player = False
        if self.total_players == 1:
            return True
        next_index = self.current_player_index
        while not found_next_player:
            next_index += 1
            if next_index >= self.total_players:
                next_index = 0
            if next_index == original_index:
                return False
            new_player_data = players.filter('play_index', next_index).get()
            if not new_player_data.eliminated:
                found_next_player == True

        self.current_player_index = next_index
        return True

    def setup(self,players):
        """ Setup the initial state. """
        raise NotImplementedError

    def get_current_player_data(self):
        players =  self.basegameplayer_set
        player_data = players.filter('play_index', self.current_player_index).get()
        return player_data

    def get_current_player(self):
        return self.get_current_player_data().player

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = dict()
        instance = self.parent()
        players = [player.get_info_dict() for player in self.basegameplayer_set]
        players[self.current_player_index]['active'] = True
        target['players'] = players
        target['current_player_index'] = self.current_player_index
        target['last_sequence_number'] = self.last_sequence_number
        target['state'] = self.state

        return target

    def is_current_player(self):
        user = UserProfile.get_current_user()
        if user != self.get_current_player():
            raise NotTurnException()


class BaseGamePlayer(polymodel.PolyModel):
    game_state = db.ReferenceProperty(BaseGameState)
    player = db.ReferenceProperty(UserProfile)
    play_index = db.IntegerProperty()
    eliminated = db.BooleanProperty(default=False)

    def get_info_dict(self, target=None):
        """ Fill info about player into a dict. """
        if target is None:
            target = dict()
        target['nickname'] = self.player.name
        target['play_index'] = self.play_index
        target['gravatar_url'] = self.player.gravatar_url()
        if self.player.user == users.get_current_user():
            target['is_me'] = True

        return target


class BaseGameAction(polymodel.PolyModel):
    game_state = db.ReferenceProperty(BaseGameState)
    sequence_number = db.IntegerProperty()
    player_index = db.IntegerProperty()
    new_state = db.StringProperty()
    action_type = 'invalid'

    def get_info_dict(self, target=None):
        """ Fill info about action into a dict. """
        if target is None:
            target = dict()
        target['player_index'] = self.player_index
        target['sequence_number'] = self.sequence_number
        if self.new_state != None:
            target['new_state'] = self.new_state
        target['action_type'] = self.action_type

        return target


class StateChangeAction(BaseGameAction):
    action_type = 'state_change'


class BaseGameInstance(polymodel.PolyModel):
    state = db.StringProperty(required=True, choices=set(["open", "playing", "finished"]))
    created = db.DateProperty(required=True)
    players = db.ListProperty(db.Key) # Keys for UserProfile
    current_state = db.ReferenceProperty(BaseGameState)
    game_name = 'basegame' # This *MUST* be the same as gamename
    human_name = 'Base Game'
    max_players = 2
    min_players = 1

    def start_game(self):
        # Check if the game can be started
        if self.state != "open":
            return False

        if len(self.players) < self.min_players:
            return False

        # Set the current to the initial state
        new_state = self.game_state_type(parent=self,key_name='state')
        players = []
        for i, player in enumerate(self.players):
            players.append(self.game_player_type(
                parent=self,
                game_state=new_state,
                player=player,
                play_index=i
                ))
        new_state.total_players = len(players)
        new_state.setup(players)
        self.current_state = new_state
        self.state = "playing"
        new_state.put()
        db.put(players)
        self.put()
        return self.current_state

    def finish_game(self):
        self.state = "finished"

    def add_user(self, user):
        # Check if the game can be joined
        if self.state != "open":
            return False

        user_key = user.key()

        # Check if the user is already joined
        if user_key in self.players:
            return False

        self.players.append(user_key)
        self.put()
        return True

    def resolve_players(self):
        return UserProfile.get(self.players)
