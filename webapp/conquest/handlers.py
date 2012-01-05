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
        instance = ConquestGameInstance(state = 'open',
                                        created = now,
                                        players = [user.key()])
        instance.put()
        return webapp2.redirect_to('lobby')

class ConquestGameInfoHandler(GameInfoHandler):
    @login_required
    def get_page(self, game_instance):
        self.prepare_context(game_instance)

        self.render_response('game_info.html')

class ConquestGamePlayHandler(GamePlayHandler):

    def __init__(self, request, response):
        GamePlayHandler.__init__(self, request, response)

        self.postHandlers['place'] = self.make_action(ConquestGameState.place_action)
        self.postHandlers['reinforce'] = self.make_action(ConquestGameState.reinforce_action)
        self.postHandlers['attack'] = self.make_action(ConquestGameState.attack_action)
        self.postHandlers['end_attack'] = self.make_action(ConquestGameState.end_attack_action)
        self.postHandlers['move'] = self.make_action(ConquestGameState.move_action)

    def get_page(self, game_instance):
        game_state = game_instance.current_state

        self.prepare_context(game_instance)
        self.render_response('play_conquest.html')

    def make_action(self, target):
        def run_action(game_instance):
            game_state = game_instance.current_state
            new_action = target(game_state, self.request)
            self.post_action(game_state, new_action)
        return run_action
