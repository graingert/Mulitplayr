from google.appengine.ext import db
from google.appengine.api import users

class UserProfile(db.Model):
    name = db.StringProperty()
    user = db.UserProperty()

    @classmethod
    def get_current_user(cls):
        gae_user = users.get_current_user()
        our_user = UserProfile.get_or_insert(gae_user.user_id(), user=gae_user, name="n00bie {0}".format(gae_user.user_id()))
        return our_user
