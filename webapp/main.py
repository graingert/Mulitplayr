import webapp2
from base import BaseHandler

from handler.test import MainPage


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
