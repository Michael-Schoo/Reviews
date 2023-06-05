from flask import redirect
from tools.jwt_token import delete_auth_cookie
from views.auth import auth_bp


@auth_bp.route('/logout', methods=['GET'])
def logout():
    """
    Logout route
    """
    # remove cookies for the user and redirect to home page
    return delete_auth_cookie(redirect('/'))

