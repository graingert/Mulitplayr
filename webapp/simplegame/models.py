import webapp2

from google.appengine.ext import db

from basegame.models import BaseGameInstance, BaseGameState

class SimpleGameState(BaseGameState):
    current_number = db.IntegerProperty()

class SimpleGameInstance(BaseGameInstance):
    current_state = db.ReferenceProperty(SimpleGameState)
