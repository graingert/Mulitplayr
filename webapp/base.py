import webapp2

from webapp2_extras import jinja2

def jinja2_fact(app):
    config = {
        'globals':{
            'uri_for':webapp2.uri_for,
        },
    }
    return jinja2.Jinja2(app, config=config)

class BaseHandler(webapp2.RequestHandler):

    context = dict()

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app, factory=jinja2_fact)

    def render_response(self, _template, context = None):
        # Renders a template and writes the result to the response.
        if not context is None:
            rv = self.jinja2.render_template(_template, **context)
        else:
            rv = self.jinja2.render_template(_template, **self.context)
        self.response.write(rv)
