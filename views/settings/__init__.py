from flask import Blueprint
from views import main_blueprint as bp

# the settings blueprint (extends main blueprint)
settings_bp = Blueprint('settings', __name__,)
bp.register_blueprint(settings_bp)

# all settings routes
from . import settings, details, make_2fa, password
