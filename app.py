from flask import Flask

# the flask extensions
from flask_cors import CORS
from flask_migrate import Migrate
from flask_qrcode import QRcode
from flask_minify import Minify
from flask_moment import Moment

# import other useful libraries
from models import db
from config import Config
from tools.template import render_user_template

# initialize the app (and the extensions)
app = Flask(__name__)
CORS(app)
QRcode(app)
Minify(app=app, html=True, js=True, cssless=True)
moment = Moment(app)
moment.init_app(app)
app.config.from_object(Config)

# initialize the database
db.app = app
db.init_app(app)
migrate = Migrate(app, db)
with app.app_context(): db.create_all()
    

# add the error handlers
@app.errorhandler(404)
def not_found(e):
    """Page not found."""
    print(e)
    return render_user_template("errors/404.html", error=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Internal server error."""
    print(e)
    return render_user_template("errors/500.html", error=e), 500

