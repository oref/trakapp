import sqlite3, re, sys
from flask import render_template, g
from . import routes

database = "sample.db"

@routes.route('/')
def home():
    g.db = connect_db()
    cur = g.db.execute('select * from posts')
    posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('index.html', posts=posts)

def connect_db():
    return sqlite3.connect(database)
