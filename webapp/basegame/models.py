import webapp2

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

class BaseGameInstance(polymodel.PolyModel):
    state = db.StringProperty(required=True, choices=set(["open", "playing", "finished"]))
    created = db.DateProperty(required=True)
    participants = db.ListProperty(users.User)
