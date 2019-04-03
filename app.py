# Import the Flask class from the flask module
import os
import sqlite3, re, sys
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session, flash, g, Blueprint
from routes import *

# Create teh application object
app = Flask(__name__)
app.register_blueprint(routes)
app.database = 'sample.db'
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY")
app.title='trak'

@app.context_processor
def logo_route():
    rule = request.url_rule
    if len(rule.rule) == 1:
        rule = '/welcome'
    return dict(end_path=rule)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

# Use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    g.db = connect_db()
    cur = g.db.execute('select * from posts')
    posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
    print(posts)
    g.db.close()
    return render_template('index.html', posts=posts)

def connect_db():
    return sqlite3.connect(app.database)

# Start the server with the 'run()' mehtod
if __name__ == '__main__':
   #if os.path.exists('client_id.json') == False:
   #    print('Client secrets file (client_id.json) not found in the app path.')
   #    exit()
   #import uuid
   #app.secret_key=(str(uuid.uuid4()))
    app.run(debug=True)
