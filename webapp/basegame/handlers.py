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
