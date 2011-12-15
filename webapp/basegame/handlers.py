import webapp2

from base import BaseHandler
from webapp2_extras.appengine.users import login_required

from models import *

def load_inherited_models(app):
    for model in app.config['game_models']:
        webapp2.import_string(model)

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
        context = {'message' : self.try_game_start(game_id) != False}
        self.render_response('index.html', **context)

    def try_game_start(self, game_id):
        game_id = int(game_id)
        if not game_id:
            return False

        game_instance = BaseGameInstance.get_by_id(game_id)
        if not game_instance:
            return False

        return game_instance.start_game()
