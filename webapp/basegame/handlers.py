import webapp2

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
        context = {}
        context['games'] = BaseGameInstance.all().fetch(50)
        self.render_response('lobby.html', **context)

class StartGameHandler(BaseHandler):
    
    @login_required
    def get(self, game_id):
        load_inherited_models(self.app)
        context = {'message' : get_game_instance(game_id).start_game() != False}
        self.render_response('index.html', **context)

class JoinGameHandler(BaseHandler):

    @login_required
    def get(self, game_id):
        load_inherited_models(self.app)
        user = users.get_current_user()
        context = {}
        context['message'] = get_game_instance(game_id).add_user(user)
        self.render_response('index.html', **context)

class GameInfoHandler(BaseHandler):

    @login_required
    def get(self, game_id):
        load_inherited_models(self.app)

        game_instance = get_game_instance(game_id)

        context = {}
        game_instance.prepare_info_context(context)
        context['game'] = game_instance
        self.render_response('game_info.html', **context)
