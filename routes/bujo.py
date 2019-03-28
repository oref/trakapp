from flask import render_template, redirect, url_for, flash, request, session, flash, g, Blueprint
from routes import *

@routes.route('/bujo')
def bujo():
    return render_template('bujo.html')

def welcome_user():
    if session['logged_in']:
        welcome_status = 'Welcome {0}'.format(session['user'])
    else:
        welcome_status = 'You are not logged in'
        return dict(welcome=welcome_status)

