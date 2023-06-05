from flask import jsonify, redirect
from pyotp import random_base32, TOTP
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import wants_json_response
from views.settings import settings_bp
from app import db


@settings_bp.route('/settings', methods=['GET'])
def profile():
    """
    User settings route
    """

    # get user
    user = get_auth_user()

    # if the user wants a json response, return json (including error if not logged in)
    if wants_json_response():
        if user is None: return jsonify(error="Unauthorized"), 401
        return jsonify(user.to_dict())
    
    # if the user is not logged in, redirect to the login page
    if user is None: return redirect('/login')

    # generate 2fa secret
    secret = random_base32()
    totp = TOTP(secret)
    qr_url = totp.provisioning_uri(user.email, issuer_name="Flask 2fa")

    # set the user's proposed_otp_secret to the secret just made
    user.proposed_otp_secret = secret
    db.session.commit()

    # show the settings page
    return render_user_template("settings.html", user=user, qr_url=qr_url)
