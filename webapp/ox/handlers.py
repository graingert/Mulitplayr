import webapp2
import datetime
import json

from google.appengine.api import users
from google.appengine.ext.db import Key

from base import BaseHandler, JSONEncoderGAE
from models import *
from profile.models import *
from basegame.handlers import *

class NewGameHandler(BaseHandler):
    def get(self):
        user = UserProfile.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        now = datetime.datetime.now().date();
        instance = OxInstance(state = 'open',
                              created = now,
                              players = [user.key()])
        instance.put()
        return webapp2.redirect_to('lobby')

class OxInfoHandler(GameInfoHandler):
    @login_required
    def get_page(self, game_instance):
        self.prepare_context(game_instance)

        self.render_response('game_info.html')

class OxPlayHandler(GamePlayHandler):

    def __init__(self, request, response):
        GamePlayHandler.__init__(self, request, response)

        self.postHandlers['place'] = self.place_action

    def get_page(self, game_instance):
        game_state = game_instance.current_state

        self.prepare_context(game_instance)
        self.render_response('play_ox.html')

    def place_action(self, game_instance):
        game_state = game_instance.current_state
        new_action = game_state.place_action(int(self.request_data['position']))
        self.post_action(game_state, new_action)
