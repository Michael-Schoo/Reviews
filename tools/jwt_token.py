# A file for making JWT tokens and verifying them

from datetime import datetime
from flask import Response, request
import jwt
from models import User
from config import Config


def create_user_token(user: User):
    """
    Create a JWT token for a user
    """
    payload = {
        "sub": user.id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + Config.JWT_AGE,
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS512")
    return token


def verify_token(token):
    """
    Verify a JWT token
    """
    try:
        # jwt verifies the expiry time
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS512"])      
         
        return payload

    except jwt.InvalidTokenError as e:
        print(e)
        return None
    

def set_auth_cookie(resp: Response, token, temp=False):
    """
    Set a cookie with the JWT token
    """
    resp.set_cookie('token', token, max_age=Config.JWT_AGE)
    return resp


def get_auth_user() -> User:
    """
    Get the user from the request
    """
    token = request.headers.get('Authorization') or request.cookies.get('token')
    if token is None:
        return None
    
    payload = verify_token(token)
    if payload is None:
        return None
    
    user: User = User.query.get(payload['sub'])
    return user
   
def delete_auth_cookie(resp: Response):
    """
    Delete the auth cookie
    """
    resp.set_cookie('token', '', expires=0)
    return resp
