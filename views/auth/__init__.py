from flask import Blueprint, jsonify
from sqlalchemy import func
from models import User
from views import main_blueprint as bp

# the auth blueprint (extends main blueprint)
auth_bp = Blueprint('auth', __name__,)
bp.register_blueprint(auth_bp)

# all items routes
from . import login, register, logout

# another route (it is small so we can keep it here)
@auth_bp.route('/verify_username/<username>', methods=['GET'])
def verify_username(username):
    """
    Verify username route
    """
    # check if username is taken
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
    if user is not None:
        return jsonify(error="Username taken"), 400
    return jsonify(success=True)
