from flask import render_template, redirect, url_for, flash, request, session, flash, g, Blueprint
from . import routes
from routes import *

@routes.route('/profile')
def profile():
    if session['logged_in']:
        return render_template('profile.html')
    else:
        return render_template('login.html')
