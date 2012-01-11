import webapp2
from base import BaseHandler
from basegame.handlers import find_game_instance_classes
class MainPage(BaseHandler):
    """
    Handler for starting a new game.

    This offers a listing of the avaible games and forwards to the
    appropriate new game URI for that game
    """

    def get(self):
        games = find_game_instance_classes(self.app)
        games = sorted(games,key=lambda x: x.human_name)
        self.context['games'] = games
        self.render_response("index.html")

