import webapp2
import datetime

from google.appengine.api import users
from google.appengine.ext.db import Key

from base import BaseHandler
from models import SimpleGameInstance
from basegame.handlers import *

class NewGameHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        now = datetime.datetime.now().date();
        instance = SimpleGameInstance(state = 'open',
                                      created = now,
                                      players = [user])
        instance.put()
        return webapp2.redirect_to('lobby')

class SimpleGameInfoHandler(GameInfoHandler):
    @login_required
    def get(self, game_id):
        game_instance = get_game_instance(game_id)

        self.prepare_context(game_instance)

        self.render_response('game_info.html')

class SimpleGamePlayHandler(GamePlayHandler):
    @login_required
    def get(self, game_id):
        game_instance = get_game_instance(game_id)
        game_state = game_instance.current_state

        self.prepare_context(game_instance)
        self.render_response('play.html')
