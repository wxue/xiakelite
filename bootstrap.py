#!/usr/bin/env python

""" 
For more information: http://pythonhosted.org//Flask-Bootstrap/index.html 
"""

import os
from wsgiref.handlers import CGIHandler
from utils import adjust_sys_path

adjust_sys_path()

from app import create_app
from werkzeug_debugger_appengine import get_debugged_app

def main():
    app = create_app()
    # If we're on the local server, let's enable Flask debugging.
    if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
        app.debug = False
        app = get_debugged_app(app)
    CGIHandler().run(app)

if __name__ == '__main__':
    main()
