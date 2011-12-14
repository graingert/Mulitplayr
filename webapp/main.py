import webapp2

config = {
    'game_models' :
    [
        'simplegame.models'
    ]
}

app = webapp2.WSGIApplication([
    ('/', 'handler.test.MainPage'),
    ('/newgame', 'simplegame.handlers.NewGameHandler'),
    ('/listgame', 'basegame.handlers.LobbyHandler'),
    ('/startgame', 'simplegame.handlers.StartGameHandler'),
    ('/joingame', 'simplegame.handlers.JoinGameHandler')
], debug=True, config=config)
