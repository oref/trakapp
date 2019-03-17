# Import the Flask class from the flask module
import sqlite3, re, sys
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session, flash, g

# Create teh application object
app = Flask(__name__)

app.secret_key = "my precious"
app.database = "sample.db"

@app.context_processor
def logo_route():
    rule = request.url_rule
    if len(rule.rule) == 1:
        rule = '/life'
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
#@login_required
def home():
    g.db = connect_db()
    cur = g.db.execute('select * from posts')
    posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
    print(posts)
    g.db.close()
    return render_template('index.html', posts=posts)

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
#@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('welcome'))

def connect_db():
    return sqlite3.connect(app.database)

# Start the server with the 'run()' mehtod
if __name__ == '__main__':
    app.run(debug=True)
