import webapp2

config = {
    'game_models' :
    [
        'simplegame.models'
    ]
}

app = webapp2.WSGIApplication([
    webapp2.Route('/', 'handler.test.MainPage'),
    webapp2.Route('/lobby/', 'basegame.handlers.LobbyHandler','lobby'),
    webapp2.Route('/newgame/', 'simplegame.handlers.NewGameHandler', 'newgame'),
    webapp2.Route('/game/<game_id>/', 'basegame.handlers.GameInfoHandler', 'gameinfo'),
    webapp2.Route('/game/<game_id>/play/', 'basegame.handlers.GamePlayHandler', 'gameplay'),
    webapp2.Route('/game/simple/<game_id>/', 'simplegame.handlers.SimpleGameInfoHandler', 'simplegameinfo'),
    webapp2.Route('/game/simple/<game_id>/play/', 'simplegame.handlers.SimpleGamePlayHandler', 'simplegameplay'),
], debug=True, config=config)
