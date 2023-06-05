from flask import Blueprint
from views import main_blueprint as bp

# the items blueprint (extends main blueprint)
item_bp = Blueprint('items', __name__,)
bp.register_blueprint(item_bp)

# all items routes
from . import item, new_item, items, recommend_new_item
