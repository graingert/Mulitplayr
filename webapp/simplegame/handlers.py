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
        return webapp2.redirect_to('lobby')

class JoinGameHandler(BaseHandler):
    def get(self, game_id):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        game_id = int(game_id)
        context = {'message' : "Unknown Game"}
        if game_id:
            game_instance = SimpleGameInstance.get_by_id(game_id)
            if game_instance:
                context['message'] = self.try_join(game_instance, user)
        self.render_response('index.html', **context)
    def try_join(self, game_instance, user):
        if game_instance.add_user(user):
            return ("Joined")
        else:
            return ("Can't Join")
