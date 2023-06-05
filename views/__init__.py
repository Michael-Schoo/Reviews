from flask import Blueprint

# the main blueprint
main_blueprint = Blueprint('main', __name__,)

# the pages and sub-blueprints to include
from . import index, auth, user, settings, items, collections, comments
