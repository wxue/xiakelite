"""
Flask Documentation:       http://flask.pocoo.org/docs/
Jinja2 Documentation:      http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:    http://werkzeug.pocoo.org/documentation/
GAE Python Documentation:  http://code.google.com/appengine/docs/python/

This file creates your application.
"""

from flask import Flask
from views import views
from utils import format_date, pygments_markdown, link_tags, get_comment_count
import settings

def create_app():
    """
    Create your application. Files outside the app directory can import
    this function and use it to recreate your application -- both
    bootstrap.py and the `tests` directory do this.
    """
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_module(views)
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['pygments_markdown'] = pygments_markdown
    app.jinja_env.filters['link_tags'] = link_tags
    app.jinja_env.filters['get_comment_count'] = get_comment_count
    return app
