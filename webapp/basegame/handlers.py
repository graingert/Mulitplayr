import webapp2
import json

from base import BaseHandler, JSONEncoderGAE
from webapp2_extras.appengine.users import login_required

from models import *

class InvalidGameIdException(Exception):
    pass

class NotTurnException(Exception):
    pass


def load_inherited_models(app):
    """ Load correct modules to resolve polymodels """
    for model in app.config['game_models']:
        webapp2.import_string(model)


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

    @login_required
    def get(self):
        load_inherited_models(self.app)
        self.context['games'] = BaseGameInstance.all()
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
        user = users.get_current_user()
        if user is None:
            return #TODO need error

        game_instance = get_game_instance(game_id)

        action = self.request.get('action')
        self.postHandlers[action](game_instance)

    def join_action(self, game_instance):
        user = users.get_current_user()
        result = {}
        result['success'] = game_instance.add_user(user)
        self.response.write(json.dumps(result))

    def start_action(self, game_instance):
        user = users.get_current_user()
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
            'state' : self.get_state,
            'actions' : self.get_actions,
        }

    def prepare_context(self, game_instance):
        """ Append base information to the render context """
        game_state = game_instance.current_state
        self.context['game'] = game_instance
        self.context['state'] = game_state
        self.context['current_player'] = game_state.current_player

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

    def not_turn(self):
        result = {}
        result['error'] = 'not-turn'
        self.response.write(json.dumps(result))

    def post(self, game_id):
        """ Dispatch post actions to correct handler """
        user = users.get_current_user()
        if user is None:
            return #TODO need error

        game_instance = get_game_instance(game_id)

        action = self.request.get('action')
        try:
            self.postHandlers[action](game_instance)
        except NotTurnException:
            self.not_turn()

    def get_state(self, game_instance):
        """ Outputs JSON data about the state """
        data = game_instance.current_state.get_info_dict()
        self.response.write(json.dumps(data, cls=JSONEncoderGAE))

    def get_actions(self, game_instance):
        """ Gets a set of actions """
        state = game_instance.current_state
        # Get the sequence number to fetch from
        try:
            since = int(self.request.get('since'))
        except ValueError:
            since = -1
        # Fetch the sequence query
        actions = state.get_actions_since(since)
        # Build the response data
        action_data = [action.get_info_dict() for action in actions]
        data = {'actions' : action_data}
        # Output the JSON
        self.response.write(json.dumps(data, cls=JSONEncoderGAE))
