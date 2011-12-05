import webapp2

app = webapp2.WSGIApplication([
    ('/', 'handler.test.MainPage'),
    ('/channel-test', 'gamebase.handlers.ChannelTest'),
    ('/channel-test/sendmessage', 'gamebase.handlers.SendMessage'),
], debug=True)
