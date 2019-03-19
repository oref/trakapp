from flask import render_template, redirect, url_for, flash, request, session, flash, g, Blueprint
from . import routes
from functools import wraps
import sqlite3, re, sys
from routes import *

#@routes.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid credentials. Please try again'
        else:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

#@routes.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were just loggedout!')
    return redirect(url_for('welcome'))


