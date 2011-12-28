import webapp2
import datetime
import json

from google.appengine.api import users
from google.appengine.ext.db import Key

from base import BaseHandler, JSONEncoderGAE
from models import *
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
    def get_page(self, game_instance):
        self.prepare_context(game_instance)

        self.render_response('game_info.html')

class SimpleGamePlayHandler(GamePlayHandler):

    def __init__(self, request, response):
        GamePlayHandler.__init__(self, request, response)

        self.postHandlers['guess'] = self.guess_action

    def get_page(self, game_instance):
        game_state = game_instance.current_state

        self.prepare_context(game_instance)
        self.render_response('play_simple.html')

    def guess_action(self, game_instance):
        # Get State
        game_state = game_instance.current_state

        action = game_state.guess_action(int(self.request.get('guess')))

        # Store data
        action.put()
        game_state.put()

        # Construct result
        result = {}
        result['guessed'] = action.guessed_number
        result['match'] = action.guessed_number == game_state.correct_number
        result['action'] = action.get_info_dict()
        result['state'] = game_state.get_info_dict()
        self.response.write(json.dumps(result, cls=JSONEncoderGAE))
