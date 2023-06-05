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


@settings_bp.route('/settings/details', methods=['POST', 'PATCH'])
def settings_details():
    """
    Change user details (username, email, password)
    """

    # get user (if not logged in, redirect to login page)
    user = get_auth_user()
    if user is None:
        if wants_json_response(): return jsonify(error="Unauthorized"), 401
        return redirect('/login')
    
    # get the form data
    data = get_form()
    username = data.get("username")
    email = data.get("email")
    name = data.get("name")

    # the issues dict will contain any issues with the data
    issues = {}

    # check the username and email for html injection
    if (username != escape(username) or email != escape(email) ):
        return jsonify(error="HTML injection?"), 400

    # Check if a user already exists with that new username
    check_user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
    if check_user is not None and check_user.id != user.id:
        issues['invalid_username'] = "already_registered"
    
    # check if email already used by another user
    check_user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
    if check_user is not None and check_user.id != user.id:
        issues['invalid_email'] = "already_registered"
    
    # username regex - 3-20 chars, only letters, numbers, and underscores (case insensitive)
    # ^[a-zA-Z0-9_]{3,20}$
    check_user = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
    if not check_user.match(username) and not 'invalid_username' in issues:
        issues['invalid_username'] = "invalid_format"

    # email regex - email@domain.tld
    # ^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$
    regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if not regex.match(email):
        issues['invalid_email'] = "invalid_format"

    # check that all fields are filled in
    if not username: issues['invalid_username'] = "required"
    if not email: issues['invalid_email'] = "required"
    if not name: issues['invalid_name'] = "required"

    # if there are any issues, return them
    if len(issues) > 0:
        if wants_json_response(): return jsonify(issues), 400
        return jsonify(issues), 400
    
    # update user (now that we know the data is valid)
    user.username = username
    user.email = email
    user.name = name
    db.session.commit()
    
    # return success or redirect back to settings page
    if wants_json_response(): return jsonify(success=True)
    return redirect('/settings')
