import webapp2
import random

from google.appengine.ext import db
from google.appengine.api import users

from basegame.models import *
from profile.models import *

def load_contries():
	contries = csv.DictReader(open("/static/board/indexmapping.csv"))
	for country in contries:
		country["index"] -= 1
		country["id"] = country["label"].lower()


class ConquestGameState(BaseGameState):
    possible_states = BaseGameState.possible_states | set([
        'place','reinforce','attack','attack_victory','fortify'])
    # State required here for possible_states support
    state = db.StringProperty(choices=possible_states, default='init')
    territory_units = db.ListProperty(int)
    territory_player = db.ListProperty(int)
    users_placed = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = dict()
        BaseGameState.get_info_dict(self, target)

        target['territory_units'] = self.territory_units
        target['territory_player'] = self.territory_player

        return target

    def setup(self, players):
        """ Setup the initial state. """
        self.check_state('init')

        self.users_placed = 0
        for territory in range(42):
            self.territory_units.append(0)
            self.territory_player.append(-1)
        
        for player in players:
            player.owned_armies = 50 - 5 * self.total_players

        self.state = 'place'

    def place_action(self, request):
        """ Place the units at the requested territory """
        self.check_state('place')
        self.is_current_player()

        placements = request.POST.getall('placements[]')

        action = PlaceAction(parent = self)
        self.add_action(action)
        player_data = self.get_current_player_data()

        total_units_placed = 0
        for i,placement in enumerate(placements):
            num_placed = int(placement)
            total_units_placed += num_placed
            self.territory_units[i] = num_placed
            self.territory_player[i] = self.current_player_index
            action.placed_units.append(num_placed)
        if total_units_placed > player_data.owned_armies:
            raise InvalidActionParametersException()
        self.users_placed += 1
        if self.users_placed == self.total_players:
            action.new_state = 'reinforce'
            self.state = 'reinforce'
        self.end_turn()
        
        return action

    def reinforce_action(self, request):
        """ Add the units to the territory """
        self.check_state('reinforce')
        self.is_current_player()
        
        action = PlaceAction(parent = self)
        self.add_action(action)

        placements = request.POST.getall('placements[]')
        for i,placement in enumerate(placements):
            num_placed = int(placement)
            self.territory_units[i] += num_placed
            action.placed_units.append(num_placed)
        action.new_state = 'attack'
        self.state = 'attack'

        return action

    def attack_action(self, request):
        """ Atack a territory """
        self.check_state('attack')
        self.is_current_player()

        action = AttackAction(parent = self)
        self.add_action(action)

        action.origin = int(request.get('origin'))
        action.destination = int(request.get('destination'))
        action.units = int(request.get('units'))

        return action

    def end_attack_action(self, request):
        """ End attack move """
        self.check_state('attack')
        self.is_current_player()

        action = BaseGameAction(parent = self)
        self.add_action(action)

        action.new_state = 'fortify'
        self.state = 'fortify'

        return action

    def move_action(self, request):
        """ Move units from one territory to another """
        self.check_state('fortify')
        self.is_current_player()

        action = MoveAction(parent = self)
        self.add_action(action)

        action.new_state = 'reinforce'
        self.state = 'reinforce'

        return action

    def end_move_action(self, request):
        """ End attack move """
        self.check_state('fortify')
        self.is_current_player()

        action = BaseGameAction(parent = self)
        self.add_action(action)

        action.new_state = 'reinforce'
        self.state = 'reinforce'

        return action


class ConquestGamePlayer(BaseGamePlayer):
    owned_armies = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about player into a dict. """
        if target is None:
            target = dict()
        BaseGamePlayer.get_info_dict(self, target)

        target['owned_armies'] = self.owned_armies

        return target


class ConquestGameInstance(BaseGameInstance):
    info_redirect = "conquestgameinfo"
    play_redirect = "conquestgameplay"

    game_player_type = ConquestGamePlayer
    game_state_type = ConquestGameState


class PlaceAction(BaseGameAction):
    placed_units = db.ListProperty(int)

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        target['placed_units'] = self.placed_units
        target['action_type'] = 'place'
        return target


class AttackAction(BaseGameAction):
    origin = db.IntegerProperty()
    destination = db.IntegerProperty()
    units = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        target['origin'] = self.origin
        target['destination'] = self.destination
        target['units'] = self.units
        target['action_type'] = 'attack'
        return target


class MoveAction(BaseGameAction):
    origin = db.IntegerProperty()
    destination = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        target['origin'] = self.origin
        target['destination'] = self.destination
        target['action_type'] = 'attack'
        return target
