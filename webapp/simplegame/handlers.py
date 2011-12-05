import webapp2
import datetime

from google.appengine.api import users

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
        self.response.out.write("Lol" + str(instance))
