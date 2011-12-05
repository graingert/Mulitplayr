import webapp2
from google.appengine.api import channel
from google.appengine.api import users
from base import BaseHandler

class ChannelTest(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        
        token = str(channel.create_channel(user.user_id()))

        context = {'message':user.user_id(),
                   'channel_token' : token
                  }
        self.render_response('channeltest.html', **context)

class SendMessage(BaseHandler):
    def post(self):
        token = self.request.get('token')
        message = self.request.get('message')
        #if token and message:
        channel.send_message(token, message)
        print "ok"
        return
        
