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
        for instance in result:
            self.response.out.write(str(instance.key().id_or_name()) + '\n')

class StartGameHandler(BaseHandler):
    def get(self):
        game_id = int(self.request.get('id'))
        if game_id:
            game_instance = SimpleGameInstance.get_by_id(game_id)
            if game_instance:
                game_instance.start_game()
                self.response.out.write(game_instance.key())
