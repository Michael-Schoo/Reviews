from flask import Blueprint
from views import main_blueprint as bp

# the collections blueprint (extends main blueprint)
collection_bp = Blueprint('collections', __name__)
bp.register_blueprint(collection_bp)

# all items routes
from . import collection, collections, collection_item, new_collection, fork_collection, like_collection


