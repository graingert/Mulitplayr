import webapp2
import json

from base import BaseHandler, JSONEncoderGAE
from webapp2_extras.appengine.users import login_required

from models import *

class ProfileViewHandler(BaseHandler):
    """
    View request handler for user profiles
    """

    @login_required
    def get(self):
        self.render_response('profile_view.html')

class ProfileEditHandler(BaseHandler):
    """
    Edit request handler for user profiles
    """

    @login_required
    def get(self):
        self.render_response('profile_edit.html')

    def post(self):
        user = UserProfile.get_current_user()
        # Set the new name, or pass through if none is set in the POST
        user.name = self.request.get("name", default_value=user.name)
        user.put()

        self.context["result"] = "Success" # TODO: actually check this
        self.render_response('profile_edit.html')
