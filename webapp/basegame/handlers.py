import webapp2
import json

from base import BaseHandler
from webapp2_extras.appengine.users import login_required

from models import *

class InvalidGameIdException(Exception):
    pass

def load_inherited_models(app):
    for model in app.config['game_models']:
        webapp2.import_string(model)

def get_game_instance(game_id):
    game_id = int(game_id)
    if not game_id:
        raise InvalidGameIdException()

    game_instance = BaseGameInstance.get_by_id(game_id)
    if not game_instance:
        raise InvalidGameIdException()

    return game_instance

class LobbyHandler(BaseHandler):

    @login_required
    def get(self):
        load_inherited_models(self.app)
        self.context['games'] = BaseGameInstance.all().fetch(50)
        self.render_response('lobby.html')

class GameInfoHandler(BaseHandler):

    def __init__(self, request, response):
        self.initialize(request, response)
        self.actionHandlers = {
            'join' : self.join_action,
            'start' : self.start_action
        }

    @login_required
    def get(self, game_id):
        load_inherited_models(self.app)
        game_instance = get_game_instance(game_id)

        self.redirect_to(game_instance.info_redirect, game_id = game_id)

    def prepare_context(self, game_instance):
        self.context['game'] = game_instance
        self.context['play_redirect'] = game_instance.play_redirect

    def post(self, game_id):

        user = users.get_current_user()
        if user is None:
            return #TODO need error

        game_instance = get_game_instance(game_id)

        action = self.request.get('action')
        self.actionHandlers[action](game_instance)

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

    def prepare_context(self, game_instance):
        game_state = game_instance.current_state
        self.context['game'] = game_instance
        self.context['state'] = game_state
        self.context['current_player'] = game_state.current_player
