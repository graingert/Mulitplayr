import webapp2

config = {
    # Games config storage.
    # Key is the base path ('conquest' goes to '/game/conquest/')
    # Properties within are used for other things (model loading,
    # human readable game names, etc)
    'games': {
        'conquest': {
            'model': 'conquest.models',
        },
        'simple': {
            'model': 'simplegame.models',
        },
        'ox': {
            'model': 'ox.models',
        },
    },
    'appstats': False
}

app = webapp2.WSGIApplication([
    webapp2.Route('/', 'handler.test.MainPage'),
    webapp2.Route('/lobby/', 'basegame.handlers.LobbyHandler','lobby'),
    webapp2.Route('/newgame/', 'basegame.handlers.NewGameHandler', 'newgame'),
    webapp2.Route('/game/active', 'basegame.handlers.ActiveGamesHandler'),
    webapp2.Route('/game/<game_id>/', 'basegame.handlers.GameInfoHandler', 'gameinfo'),
    webapp2.Route('/game/<game_id>/play/', 'basegame.handlers.GamePlayHandler', 'gameplay'),
    webapp2.Route('/game/simple/newgame/', 'simplegame.handlers.NewGameHandler', 'newgame-simple'),
    webapp2.Route('/game/simple/<game_id>/', 'simplegame.handlers.SimpleGameInfoHandler', 'simplegameinfo'),
    webapp2.Route('/game/simple/<game_id>/play/', 'simplegame.handlers.SimpleGamePlayHandler', 'simplegameplay'),
    webapp2.Route('/game/ox/newgame/', 'ox.handlers.NewGameHandler', 'newgame-ox'),
    webapp2.Route('/game/ox/<game_id>/', 'ox.handlers.OxInfoHandler', 'oxgameinfo'),
    webapp2.Route('/game/ox/<game_id>/play/', 'ox.handlers.OxPlayHandler', 'oxgameplay'),
    # For the newgame page to work newgame routes must have the name 'newgame-<game_name>'
    webapp2.Route('/game/conquest/newgame/', 'conquest.handlers.NewGameHandler', 'newgame-conquest'),
    webapp2.Route('/game/conquest/<game_id>/', 'conquest.handlers.ConquestGameInfoHandler', 'conquestgameinfo'),
    webapp2.Route('/game/conquest/<game_id>/play/', 'conquest.handlers.ConquestGamePlayHandler', 'conquestgameplay'),
    webapp2.Route('/profile/', 'profile.handlers.ProfileViewHandler'),
    webapp2.Route('/profile/edit', 'profile.handlers.ProfileEditHandler', name='profile-edit'),
], debug=True, config=config)

# Appstats
if config['appstats']:
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
