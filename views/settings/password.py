import re
from flask import redirect, request, jsonify
from markupsafe import escape
from sqlalchemy import func
from models import User
from tools.jwt_token import get_auth_user
from pyotp import TOTP, random_base32
from tools.template import render_user_template
from tools.tools import get_form, wants_json_response
from views.settings import settings_bp
from app import db


@settings_bp.route('/settings/password', methods=['POST', 'PATCH'])
def settings_password():
    """
    Change user password
    """

    # get user (if not logged in, redirect to login page)
    user = get_auth_user()
    if user is None:
        if wants_json_response(): return jsonify(error="Unauthorized"), 401
        return redirect('/login')
    
    # get the form data
    data = get_form()
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    confirm_password = data.get("new_password_confirm")

    # the issues dict will contain any issues with the data
    issues = {}

    # check the password and confirm password are matching
    if new_password != confirm_password:
        issues['invalid_confirm_password'] = "not_matching"

    # check if old password is correct
    if not user.check_password(old_password):
        issues['invalid_password'] = "incorrect"

    # just make sure all the fields are filled in
    if not old_password: issues['invalid_old_password'] = "required"
    if not new_password: issues['invalid_new_password'] = "required"
    if not confirm_password: issues['invalid_confirm_password'] = "required"

    # if there are any issues, return them
    if len(issues) > 0:
        if wants_json_response(): return jsonify(issues), 400
        return jsonify(issues), 400
    
    # update user (now that we know the data is valid)
    user.set_password(new_password)
    db.session.commit()

    # return success or redirect back to settings page
    if wants_json_response(): return jsonify(success=True)
    return redirect('/settings')
