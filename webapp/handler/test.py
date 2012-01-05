import webapp2
from base import BaseHandler

class MainPage(BaseHandler):
    def get(self):
        self.context['message'] = 'This is a test templated message'
        self.render_response('index.html')
