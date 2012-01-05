import webapp2

config = {
    'game_models' :
    [
        'simplegame.models',
        'conquest.models'
    ]
}

app = webapp2.WSGIApplication([
    webapp2.Route('/', 'handler.test.MainPage'),
    webapp2.Route('/lobby/', 'basegame.handlers.LobbyHandler','lobby'),
    webapp2.Route('/newgame/', 'conquest.handlers.NewGameHandler', 'newgame'),
    webapp2.Route('/game/<game_id>/', 'basegame.handlers.GameInfoHandler', 'gameinfo'),
    webapp2.Route('/game/<game_id>/play/', 'basegame.handlers.GamePlayHandler', 'gameplay'),
    webapp2.Route('/game/simple/<game_id>/', 'simplegame.handlers.SimpleGameInfoHandler', 'simplegameinfo'),
    webapp2.Route('/game/simple/<game_id>/play/', 'simplegame.handlers.SimpleGamePlayHandler', 'simplegameplay'),
    webapp2.Route('/game/conquest/<game_id>/', 'conquest.handlers.ConquestGameInfoHandler', 'conquestgameinfo'),
    webapp2.Route('/game/conquest/<game_id>/play/', 'conquest.handlers.ConquestGamePlayHandler', 'conquestgameplay'),
    webapp2.Route('/profile/', 'profile.handlers.ProfileViewHandler'),
    webapp2.Route('/profile/edit', 'profile.handlers.ProfileEditHandler', name='profile-edit'),
], debug=True, config=config)

# Appstats
from google.appengine.ext.appstats import recording
app = recording.appstats_wsgi_middleware(app)
