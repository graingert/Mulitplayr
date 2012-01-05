from google.appengine.ext import db
from google.appengine.api import users
import urllib, hashlib

class UserProfile(db.Model):
    name = db.StringProperty()
    user = db.UserProperty()

    @classmethod
    def get_current_user(cls):
        gae_user = users.get_current_user()
        if gae_user is None: # Handle not being logged in
            return None
        our_user = UserProfile.get_or_insert(
			gae_user.user_id(),
			user=gae_user,
			name=gae_user.nickname().rsplit("@",1)[0],
		)
        return our_user
    
    def gravatar_url(self, size=48, default="identicon", force_default="n", rating="g", secure=False):
		federated_image_service = "http://www.gravatar.com/avatar/"
		if secure:
			federated_image_service = "https://secure.gravatar.com/avatar/"
		gravatar_url = federated_image_service + hashlib.md5(self.user.email().lower()).hexdigest() + "?"
		gravatar_url += urllib.urlencode({
			'd':default,
			's':str(size),
			'f':force_default,
			'r':rating, 
		})
		return gravatar_url

    def __eq__(self, other):
        """ Equality is based on the GAE User """
        if (isinstance(other, UserProfile)):
            return self.user == other.user
        return NotImplemented

    def __ne__(self, other):
        """ Inequality is stupid and needs overriding too """
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
