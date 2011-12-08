import webapp2
import datetime

from google.appengine.api import users
from google.appengine.ext.db import Key

from base import BaseHandler
from models import SimpleGameInstance

class NewGameHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        now = datetime.datetime.now().date();
        instance = SimpleGameInstance(state = 'open',
                                      created = now,
                                      participants = [user])
        instance.put()
        self.response.out.write(instance.key())

class ListGameHandler(BaseHandler):
    def get(self):
        q = SimpleGameInstance.all()
        result = q.fetch(5)
        context = {'games':result}
        self.render_response('gamelist.html', **context)

class StartGameHandler(BaseHandler):
    def get(self):
        game_id = int(self.request.get('id'))
        if game_id:
            game_instance = SimpleGameInstance.get_by_id(game_id)
            if game_instance:
                self.try_game_start(game_instance)
    def try_game_start(self, game_instance):
        if game_instance.start_game():
            self.response.out.write("Started game")
        else:
            self.response.out.write("Game is not open")
