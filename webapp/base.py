import webapp2
import json

from google.appengine.api import users
from google.appengine.ext import db

from webapp2_extras import jinja2

from profile.models import UserProfile

class JSONEncoderGAE(json.JSONEncoder):

    """Encoder Compatible with GAE DB types"""

    def default(self, obj):
        """Support for GAE types"""
        if isinstance(obj, users.User):
            return obj.nickname()
        return json.JSONEncoder.default(self, obj)

def jinja2_fact(app):
    """Jinja2 factory adding required globalss"""
    config = {
        'globals':{
            'uri_for':webapp2.uri_for,
        },
    }
    return jinja2.Jinja2(app, config=config)

class BaseHandler(webapp2.RequestHandler):

    """
    Base for all handlers adding templating support.
    This code comes mostly from the webapp2 jinjia support module.
    """

    context = dict()

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app, factory=jinja2_fact)

    def render_response(self, _template, context = None):
        # Renders a template and writes the result to the response.
        if context is None:
            context = self.context
        # Put things that are needed in all templates here
        context["profile"] = UserProfile.get_current_user()
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)
