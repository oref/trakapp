from flask import Blueprint
routes = Blueprint('routes', __name__)

from .index import *
from .login import *
from .google_auth import *
from .bujo import *
from .profile import *
