from flask import render_template, redirect, url_for, flash, request, session, flash, g, Blueprint
from . import routes
from functools import wraps
import sqlite3, re, sys
from routes import *

@routes.route("/login")
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url( Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)

@app.route('/gCallback')
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has successfully authenticated our app.
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token( Auth.TOKEN_URI, client_secret=Auth.CLIENT_SECRET, authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'
