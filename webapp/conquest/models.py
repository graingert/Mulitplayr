import webapp2
import random
import csv

from google.appengine.ext import db
from google.appengine.api import users

from basegame.models import *
from profile.models import *

class TerritoryMapper():
    def __init__(self):
        self.territory_indexes = {}
        self.territory_labels = {}

        index_mapping_data = csv.DictReader(
			open("data/indexmapping.csv")
		)
        for territory in index_mapping_data:
            index = int(territory["index"])-1
            label  = territory["label"].lower().replace(" ", "-")
            self.territory_indexes[label] = index
            self.territory_labels[index] = label
    
    def get_territory_index(self, label):
        return self.territory_indexes[label]

    def get_territory_label(self, index):
        return self.territory_labels[index]

    def get_size(self):
        return len(self.territory_indexes)


def get_territory_mapper():
    app = webapp2.get_app()
    territory_mapper = app.registry.get('conquest.territory_mapper')
    if not territory_mapper:
        territory_mapper = TerritoryMapper()
        app.registry['conquest.territory_mapper'] = territory_mapper
    return territory_mapper


def attacking_phase_roll_dice(attack_armies, defend_armies):
    attack_dice = [random.randint(1, 6) for i in range(attack_armies)]
    attack_dice.sort()
    attack_dice.reverse()

    defend_dice = [random.randint(1, 6) for i in range(defend_armies)]
    defend_dice.sort()
    defend_dice.reverse()

    return [attack_dice, defend_dice]


class ConquestGameState(BaseGameState):
    possible_states = BaseGameState.possible_states | set([
        'place','reinforce','attack','attack_victory','fortify'])
    # State required here for possible_states support
    state = db.StringProperty(choices=possible_states, default='init')
    territory_units = db.ListProperty(int)
    territory_player = db.ListProperty(int)
    attack_victory_origin = db.IntegerProperty()
    attack_victory_destination = db.IntegerProperty()
    users_placed = db.IntegerProperty()

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict. """
        if target is None:
            target = dict()
        BaseGameState.get_info_dict(self, target)

        territory_mapper = get_territory_mapper()
        territories = []
        for i in range(len(self.territory_units)):
            label = territory_mapper.get_territory_label(i)
            data = {'id':label,
                    'player':self.territory_player[i],
                    'units':self.territory_units[i]
                   }
            territories.append(data)
        target['territories'] = territories

        return target

    def setup(self, players):
        """ Setup the initial state. """
        self.check_state('init')

        territory_ownership = random.shuffle(range(42))
        player = 0

        self.users_placed = 0
        for territory in range(42):
            self.territory_units.append(0)
            self.territory_player.append(player)
            player = (player + 1) % self.total_players
        
        for player in players:
            player.owned_armies = 50 - 5 * self.total_players

        self.state = 'place'

    def place_action(self, request):
        """ Place the units at the requested territory """
        self.check_state('place')
        self.is_current_player()

        placements = request['placements']

        territory_mapper = get_territory_mapper()
        player_data = self.get_current_player_data()

        action = PlaceAction(parent = self)
        self.add_action(action)

        total_units_placed = 0
        for i in range(territory_mapper.get_size()):
            action.placed_units.append(0)
        for placement in placements:
            placement_index = territory_mapper.get_territory_index(placement['id'])
            units = placement['units']
            total_units_placed += units
            action.placed_units[placement_index] = units
            self.territory_units[placement_index] = units
            self.territory_player[placement_index] = self.current_player_index
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

        placements = request['placements']
        
        territory_mapper = get_territory_mapper()
        player_data = self.get_current_player_data()

        action = PlaceAction(parent = self)
        self.add_action(action)

        total_units_placed = 0
        for i in range(territory_mapper.get_size()):
            action.placed_units.append(0)
        for placement in placements:
            placement_index = territory_mapper.get_territory_index(placement['id'])
            units = placement['units']
            total_units_placed += units
            action.placed_units[placement_index] = units
            if self.territory_player[placement_index] != self.current_player_index:
                raise InvalidActionParametersException()
            self.territory_units[placement_index] += units
        if total_units_placed > player_data.owned_armies:
            raise InvalidActionParametersException()

        action.new_state = 'attack'
        self.state = 'attack'

        return action

    def attack_action(self, request):
        """ Atack a territory """
        self.check_state('attack')
        self.is_current_player()

        territory_mapper = get_territory_mapper()

        origin = territory_mapper.get_territory_index(request['origin'])
        destination = territory_mapper.get_territory_index(request['destination'])
        attackers = int(request['attackers'])

        if self.territory_player[origin] != self.current_player_index:
            raise InvalidActionParametersException()
        if self.territory_player[destination] == self.current_player_index:
            raise InvalidActionParametersException()

        possible_attackers = min(self.territory_units[origin] - 1, 3)
        possible_defenders = min(self.territory_units[destination], 2)
        if attackers > possible_attackers:
            raise InvalidActionParametersException
        defenders = min(possible_defenders, attackers)

        attack_dice, defend_dice = attacking_phase_roll_dice(attackers, attackers)

        win_rolls = 0
        loose_rolls = 0
        while len(attack_dice) > 0 and len(defend_dice) > 0:
            if attack_dice.pop() > defend_dice.pop():
                win_rolls += 1
            else:
                loose_rolls += 1
        self.territory_units[origin] -= loose_rolls
        self.territory_units[destination] -= win_rolls

        action = AttackAction(parent = self)
        self.add_action(action)

        if self.territory_units[destination] <= 0:
            self.territory_player[destination] = self.current_player_index
            self.attack_victory_origin = origin
            self.attack_victory_destination = destination
            action.new_state = 'attack_victory'
            self.state = 'attack_victory'

        action.origin = origin
        action.destination = destination
        action.attackers = attackers
        action.attack_rolls = attack_dice
        action.defend_rolls = defend_dice

        return action
    
    def attack_victory_action(self, request):
        """ Move after win attack """
        self.check_state('attack_victory')
        self.is_current_player()

        units = int(request['units'])
        if units < 1:
            raise InvalidActionParametersException

        action = MoveAction(parent = self)
        self.add_action(action)

        action.origin = self.attack_victory_origin
        action.destination = self.attack_victory_destination
        self.territory_units[action.origin] -= units
        self.territory_units[action.destination] += units
        action.units = units

        action.new_state = 'attack'
        self.state = 'attack'

        return action

    def end_attack_action(self, request):
        """ End attack move """
        self.check_state('attack')
        self.is_current_player()

        action = StateChangeAction(parent = self)
        self.add_action(action)

        action.new_state = 'fortify'
        self.state = 'fortify'

        return action

    def move_action(self, request):
        """ Move units from one territory to another """
        self.check_state('fortify')
        self.is_current_player()

        territory_mapper = get_territory_mapper()

        origin = territory_mapper.get_territory_index(request['origin'])
        destination = territory_mapper.get_territory_index(request['destination'])
        units = int(request['units'])

        if self.territory_player[origin] != self.current_player_index:
            raise InvalidActionParametersException
        if self.territory_player[destination] != self.current_player_index:
            raise InvalidActionParametersException

        units_at_origin = self.territory_units[origin]
        if units >= units_at_origin:
            raise InvalidActionParametersException

        self.territory_units[origin] -= units
        self.territory_units[destination] += units

        action = MoveAction(parent = self)
        self.add_action(action)

        action.origin = origin
        action.destination = destination
        action.units = units

        action.new_state = 'reinforce'
        self.state = 'reinforce'
        self.end_turn()

        return action

    def end_move_action(self, request):
        """ End attack move """
        self.check_state('fortify')
        self.is_current_player()

        action = StateChangeAction(parent = self)
        self.add_action(action)

        action.new_state = 'reinforce'
        self.state = 'reinforce'
        self.end_turn()

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
    game_name = 'conquest'
    human_name = 'Conquest'
    description = """
Battle your enemies and bring your foes to their knees in this
exhilarating turn based conquest for world domination
	"""
    info_redirect = "conquestgameinfo"
    play_redirect = "conquestgameplay"

    game_player_type = ConquestGamePlayer
    game_state_type = ConquestGameState


class PlaceAction(BaseGameAction):
    placed_units = db.ListProperty(int)
    action_type = 'place'

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        territory_mapper = get_territory_mapper()
        placements = []
        for i,placement in enumerate(self.placed_units):
            if placement > 0:
                label = territory_mapper.get_territory_label(i)
                data = {'id':label,
                        'units':placement
                       }
                placements.append(data)
        target['placed_units'] = placements
        return target


class AttackAction(BaseGameAction):
    origin = db.IntegerProperty()
    destination = db.IntegerProperty()
    attackers = db.IntegerProperty()
    attack_rolls = db.ListProperty(int)
    defend_rolls = db.ListProperty(int)
    action_type = 'attack'

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        territory_mapper = get_territory_mapper()
        target['origin'] = territory_mapper.get_territory_label(self.origin)
        target['destination'] = territory_mapper.get_territory_label(self.destination)
        target['attackers'] = self.attackers
        return target


class MoveAction(BaseGameAction):
    origin = db.IntegerProperty()
    destination = db.IntegerProperty()
    units = db.IntegerProperty()
    action_type = 'move'

    def get_info_dict(self, target=None):
        """ Fill info about state into a dict """
        if target is None:
            target = {}
        BaseGameAction.get_info_dict(self, target)
        territory_mapper = get_territory_mapper()
        target['origin'] = territory_mapper.get_territory_label(self.origin)
        target['destination'] = territory_mapper.get_territory_label(self.destination)
        target['units'] = self.units
        return target
