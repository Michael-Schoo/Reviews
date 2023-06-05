from flask import redirect, request, jsonify
from tools.jwt_token import get_auth_user
from pyotp import TOTP, random_base32
from tools.template import render_user_template
from tools.tools import get_form, wants_json_response
from views.settings import settings_bp
from app import db


@settings_bp.route('/settings/2fa', methods=['POST', 'PATCH', 'GET'])
def two_factor_auth():
    """
    A page to get a qrcode for 2fa
    """

    user = get_auth_user()
    if user is None:
        # 401 Unauthorized
        return jsonify(error="Unauthorized"), 401
    
    if request.method == 'GET':
        secret = random_base32()
        totp = TOTP(secret)
        qr_url = totp.provisioning_uri(user.email, issuer_name="Flask 2fa")
        user.proposed_otp_secret = secret
        db.session.commit()

        return jsonify(qr_url=qr_url, secret=secret, already_set=(user.otp_secret is not None))
    
    # Check if 2fa token is valid
    data = get_form() 
    code = data.get('2fa_code')
    proposed_secret = user.proposed_otp_secret

    totp = TOTP(proposed_secret)
    if not totp.verify(code):
        return jsonify(error="Invalid 2fa code"), 400

    # Set 2fa secret
    user.otp_secret = proposed_secret
    db.session.commit()

    # return success or redirect back to settings page
    if wants_json_response(): return jsonify(success=True)
    return redirect('/settings')
    