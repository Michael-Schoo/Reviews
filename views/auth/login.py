from flask import make_response, redirect, render_template, request, jsonify
from sqlalchemy import func
from tools.jwt_token import create_user_token, get_auth_user, set_auth_cookie
from models import User
from tools.tools import get_form, wants_json_response
from pyotp import TOTP
from views.auth import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route
    """

    # if logged in, redirect to home page (but api access can still re-login)
    if get_auth_user() and not wants_json_response(): return redirect('/')

    # if GET, return login page
    if request.method == 'GET':
        return render_template("login.html")

    # if POST, login user
    if request.method == 'POST':

        # get the form data
        data = get_form()
        email = data.get('email')
        password = data.get('password')
        remember_me = data.get('remember_me', False)

        # Check if user exists (using email) and check password
        user: User = User.query.filter(func.lower(User.email) == func.lower(email)).first()
        if user is None or not user.check_password(password):
            # return error stating invalid email or password (don't specify which one is wrong)
            if wants_json_response(): return jsonify(error="Invalid email or password"), 401
            return render_template("login.html", invalid_creds=True, prev_data=data), 401

        # do extra checks if 2fa is enabled
        if user.otp_secret:

            # create totp object (using user's secret)
            totp = TOTP(user.otp_secret)

            # if they haven't done the 2fa yet, do it now
            if 'code' in data:
                token = data.get('code')
                
                if not totp.verify(token):
                    # return jsonify(error="Invalid 2fa token"), 401
                    token = totp.now()
                    if wants_json_response(): return jsonify(error="Invalid 2fa token"), 401
                    return render_template("login_2fa.html", invalid_code=True, placeholder_token=token, user=data), 401
                
                # success! add to cookies (that is done below)
                 
            else:
                # get the token (to show in the placeholder because convenience ~not secure~)
                token = totp.now()

                # return the 2fa page
                if wants_json_response(): return jsonify(error="2fa required", code=token), 401
                return render_template("login_2fa.html", remember_me=remember_me, placeholder_token=token, user=data)
        else:
            # add to cookies
            token = create_user_token(user)
            resp_data = redirect('/user/@me')
            if wants_json_response(): resp_data = jsonify(token=token, user=user.to_dict())
            resp = make_response(resp_data)
            set_auth_cookie(resp, token, temp=remember_me)
            return resp
