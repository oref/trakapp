import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes import *

routes = Flask(__name__)
routes.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/user.db'
db = SQLAlchemy(routes)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime,
                           default=datetime.datetime.utcnow())


basedir = os.path.abspath(os.path.dirname(__file__))
class Auth:
    CLIENT_ID = ('1065909267698-8ddem0tai2sf58vtebsb6orgluu5iv22.apps.googleusercontent.com')
    REDIRECT_URI = 'https://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google..com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'

class Config:
    APP_NAME = 'Test Google Login'
    SECRET_KEY = os.environ.get("SECRET_KEY") or "precious"

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+ os.path.join(basedir, "test.db")

class ProdConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "prod.db")

config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default" DevConfig
}
