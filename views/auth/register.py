from glob import escape
import re
from flask import make_response, redirect, render_template, request, jsonify
from sqlalchemy import func
from tools.jwt_token import create_user_token, get_auth_user, set_auth_cookie
from models import User
from app import db
from tools.tools import get_form, wants_json_response
from views.auth import auth_bp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register route
    """

    # if logged in, redirect to home page (but api access can still re-create account)
    if get_auth_user() and not wants_json_response(): return redirect('/')

    # if GET, return register page
    if request.method == 'GET':
        return render_template("register.html")
    
    # if POST, register user
    if request.method == 'POST':
        
        # get the form data
        data = get_form()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        name = data.get('name')
        
        # the issues dict will contain any issues with the data
        issues = {}

        # check for html injection
        if (username != escape(username) or email != escape(email) ):
            return jsonify(error="HTML injection?"), 400

        # Check if user exists with the same username
        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
        if user is not None:
            issues['invalid_username'] = "already_registered"
        
        # check if email already used
        user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
        if user is not None:
            issues['invalid_email'] = "already_registered"
        
        # username regex - 3-20 chars, only letters, numbers, and underscores (case insensitive)
        # ^[a-zA-Z0-9_]{3,20}$
        regex = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
        if not regex.match(username):
            issues['invalid_username'] = "invalid_format"

        # password regex - 8-50 chars
        # ^.*{8,20}$
        regex = re.compile(r"^.{8,50}$")
        if not regex.match(password):
            issues['invalid_password'] = "invalid_format"

        # email regex - email@domain.tld
        # ^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$
        regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not regex.match(email):
            issues['invalid_email'] = "invalid_format"

        # make sure all fields are filled
        if not username: issues['invalid_username'] = "required"
        if not password: issues['invalid_password'] = "required"
        if not email: issues['invalid_email'] = "required"
        if not name: issues['invalid_name'] = "required"

        # if there are any issues, return them
        if len(issues) > 0:
            if wants_json_response(): return jsonify(issues), 400
            return render_template("register.html", **issues, prev_data=data), 400


        # Create user
        user = User(username=username, email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # create the user's token
        token = create_user_token(user)

        # return the the user's page with the token in cookies (if api, return json with token)
        resp_data = redirect('/user/@me')
        if wants_json_response(): resp_data = jsonify(token=token, user=user.to_dict())
        resp = make_response(resp_data)
        set_auth_cookie(resp, token)
        return resp
            

