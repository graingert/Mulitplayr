import webapp2

app = webapp2.WSGIApplication([
    ('/', 'handler.test.MainPage'),
], debug=True)
