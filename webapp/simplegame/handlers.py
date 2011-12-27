import webapp2
import datetime
import json

from google.appengine.api import users
from google.appengine.ext.db import Key

from base import BaseHandler
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

        user = users.get_current_user()
        if user != game_state.current_player:
            raise NotTurnException()

        # Construct action
        action = SimpleGameAction(parent = game_state)
        action.guessed_number = int(self.request.get('guess'))
        game_state.add_action(action)

        # End players turn
        game_state.end_turn()

        # Store data
        action.put()
        game_state.put()

        # Construct result
        result = {}
        result['guessed'] = action.guessed_number
        result['match'] = action.guessed_number == game_state.correct_number
        result['action'] = action.get_info_dict()
        if action.guessed_number < game_state.correct_number:
            result['dir'] = "Higher"
        if action.guessed_number > game_state.correct_number:
            result['dir'] = "Lower"
        self.response.write(json.dumps(result))
