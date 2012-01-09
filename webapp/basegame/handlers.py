import webapp2
import json
import itertools

from base import BaseHandler, JSONEncoderGAE
from webapp2_extras.appengine.users import login_required

from models import *
from profile.models import *

class InvalidGameIdException(Exception):
    pass

class GameTypeNotFoundError(Exception):
    pass

def load_inherited_models(app):
    """ Load correct modules to resolve polymodels
    Returns the modules loaded
    """
    model_modules = []
    for game_name, game in app.config['games'].iteritems():
        model_modules.append(webapp2.import_string(game['model']))
    return model_modules

def find_game_instance_classes(app):
    """ Get a list of BaseGameInstance classes """
    import inspect
    game_instance_classes = []
    # Find all the model modules
    for model_module in load_inherited_models(app):
        # Grab the members of the model module
        for (name, item) in inspect.getmembers(model_module):
            # Filter the memebers - the ones that are classes, in the module
            # we're looking at that inherits from BaseGameInstance
            if inspect.isclass(item) and inspect.getmodule(item) == model_module and issubclass(item, BaseGameInstance):
                game_instance_classes.append(item)
    return game_instance_classes


def get_game_instance(game_id):
    """ Get the instance given by a game_id """
    game_id = int(game_id)
    if not game_id:
        raise InvalidGameIdException()

    game_instance = BaseGameInstance.get_by_id(game_id)
    if not game_instance:
        raise InvalidGameIdException()

    return game_instance




class LobbyHandler(BaseHandler):
    """
    Simple lobby hander.
    """
    human_game_states = {
            'playing': 'DO NOT WANT',
            'player-playing': 'Active games',
            'open': 'Available games',
            'player-open': 'Joined games',
    }

    @login_required
    def get(self):
        load_inherited_models(self.app)

        current_user = UserProfile.get_current_user()
        def group_func(x):
            state = x.state
            if current_user.key() in x.players:
                state = "player-" + state
            return LobbyHandler.human_game_states[state]

        games = BaseGameInstance.all()
        # Filter here because you can't do OR on datastore ;(
        games = [game for game in games
                if game.state == 'open'
                or (current_user.key() in game.players
                    and game.state != 'finished')]
        self.context['groupedGames'] = itertools.groupby(games,group_func)
        self.render_response('lobby.html')


class GameInfoHandler(BaseHandler):
    """
    Base handler for game info.
    """

    def __init__(self, request, response):
        self.initialize(request, response)
        self.postHandlers = {
            'join' : self.join_action,
            'start' : self.start_action
        }
        self.getHandlers = {
        }

    @login_required
    def get(self, game_id):
        """ Dispatch get actions to correct handler """
        action = self.request.get('action')

        if action == '':
            if self.get_page.__func__ == GameInfoHandler.get_page.__func__:
                self.get_page(game_id)
            else:
                game_instance = get_game_instance(game_id)
                self.get_page(game_instance)
        else:
            self.getHandlers[action](game_instance)

    def get_page(self, game_id):
        """ Redirect to correct game info URI """
        load_inherited_models(self.app)
        game_instance = get_game_instance(game_id)

        self.redirect_to(game_instance.info_redirect, game_id = game_id)

    def prepare_context(self, game_instance):
        """ Append base information to the render context """
        self.context['game'] = game_instance
        self.context['play_redirect'] = game_instance.play_redirect

    def post(self, game_id):
        """ Dispatch post actions to correct handler """
        user = UserProfile.get_current_user()
        if user is None:
            return #TODO need error

        game_instance = get_game_instance(game_id)

        action = self.request.get('action')
        self.postHandlers[action](game_instance)

    def join_action(self, game_instance):
        user = UserProfile.get_current_user()
        result = {}
        result['success'] = game_instance.add_user(user)
        self.response.write(json.dumps(result))

    def start_action(self, game_instance):
        user = UserProfile.get_current_user()
        if user.key() not in game_instance.players:
            self.error(403)
            return
        result = {}
        result['success'] = game_instance.start_game() != None
        self.response.write(json.dumps(result))


class GamePlayHandler(BaseHandler):
    """
    Base handler for game play.
    """

    def __init__(self, request, response):
        self.initialize(request, response)
        # Actions for post events
        self.postHandlers = {
        }
        # Action for get events
        self.getHandlers = {
            'update' : self.get_update,
        }

    def prepare_context(self, game_instance):
        """ Append base information to the render context """
        game_state = game_instance.current_state
        self.context['game'] = game_instance
        self.context['state'] = game_state

    @login_required
    def get(self, game_id):
        """ Dispatch get actions to correct handler """
        action = self.request.get('action')
        game_instance = get_game_instance(game_id)

        # Render page on no action specified
        if action == '':
            self.get_page(game_instance)
        else:
            self.getHandlers[action](game_instance)

    def error_responce(self, message):
        result = {}
        result['error'] = message
        self.response.write(json.dumps(result))

    def post(self, game_id):
        """ Dispatch post actions to correct handler """
        user = UserProfile.get_current_user()
        if user is None:
            self.error_responce('invalid-user')
            return

        game_instance = get_game_instance(game_id)

        self.request_data = json.loads(self.request.body)
        action = self.request_data['action']
        try:
            self.postHandlers[action](game_instance)
        except NotTurnException:
            self.error_responce('not-turn')
        except InvalidStateException:
            self.error_responce('invalid-state')
        if game_instance.current_state.state == 'finished':
            game_instance.finish_game()
            game_instance.put()

    def post_action(self, game_state, new_action):
        last_seq_num = int(self.request_data['last_sequence_number'])
        actions = game_state.get_actions_since(last_seq_num)
        # Construct result
        result = {}
        result['actions'] = [action.get_info_dict() for action in actions]
        result['actions'].append(new_action.get_info_dict())
        result['state'] = game_state.get_info_dict()
        self.response.write(json.dumps(result, cls=JSONEncoderGAE))
        # Store data
        new_action.put()
        game_state.put()

    def get_update(self, game_instance):
        """ Gets the state and actions from a given sequence number """
        state = game_instance.current_state
        try:
            seq_from = int(self.request.get('from'))
        except ValueError:
            seq_from = -1
        # Fetch the sequence query
        actions = state.get_actions_since(max(state.last_sequence_number - 5,seq_from))
        # Build the response data
        action_data = [action.get_info_dict() for action in actions]
        state_data = state.get_info_dict()
        data = {'actions' : action_data,
                'state' : state_data}
        # Output the JSON
        self.response.write(json.dumps(data, cls=JSONEncoderGAE))

class NewGameHandler(BaseHandler):
    """
    Handler for starting a new game.

    This offers a listing of the avaible games and forwards to the
    appropriate new game URI for that game
    """

    @login_required
    def get(self):
        games = find_game_instance_classes(self.app)
        games = sorted(games,key=lambda x: x.human_name)
        self.context['games'] = games
        self.render_response("new_game.html")

class ActiveGamesHandler(BaseHandler):
    """
    Handler for starting a new game.

    This offers a listing of the avaible games and forwards to the
    appropriate new game URI for that game
    """

    @login_required
    def get(self):
        load_inherited_models(self.app)

        user = UserProfile.get_current_user()
        games = list(BaseGameInstance.gql(
                "WHERE state = 'playing' AND players = :1", user).run())
        result = {'games':[]}
        for game in games:
            current_player = game.current_state.get_current_player()
            game_dict = {
                    'awaitingPlayerMove': (current_player == user),
                    'currentPlayer': current_player.name,
                    'type': game.human_name,
                    'uri': webapp2.uri_for(game.play_redirect, game_id=game.key().id())
            }
            result['games'].append(game_dict)
        self.response.write(json.dumps(result, cls=JSONEncoderGAE))
