import webapp2

config = {
    'game_models' :
    [
        'simplegame.models'
    ]
}

app = webapp2.WSGIApplication([
    webapp2.Route('/', 'handler.test.MainPage'),
    webapp2.Route('/lobby', 'basegame.handlers.LobbyHandler','lobby'),
    webapp2.Route('/newgame', 'simplegame.handlers.NewGameHandler', 'newgame'),
    webapp2.Route('/startgame/<game_id>', 'basegame.handlers.StartGameHandler', 'startgame'),
    webapp2.Route('/joingame/<game_id>', 'simplegame.handlers.JoinGameHandler', 'joingame')
], debug=True, config=config)
