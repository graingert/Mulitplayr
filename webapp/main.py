import webapp2

app = webapp2.WSGIApplication([
    ('/', 'handler.test.MainPage'),
    ('/newgame', 'simplegame.handlers.NewGameHandler')
], debug=True)
