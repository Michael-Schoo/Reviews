from flask import jsonify, redirect, request
from models import User
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import id_from_url, url_from_id, wants_json_response
from . import main_blueprint as bp
from app import db


@bp.route('/user/<user_id>', methods=['GET', 'DELETE'])
@bp.route('/user/<user_id>/delete', methods=['POST'])
def user_page(user_id):
    """
    User page route
    """

    # if the user id is @me, redirect to the user's page
    if user_id == '@me':
        user = get_auth_user()
        if user is None: return jsonify(error="Unauthorized"), 401
        return redirect('/user/' + url_from_id(user.id, user.username))
    
    # get userid from url
    id = id_from_url(user_id)

    # if userid starts with a @, get the user by username otherwise get by id
    if user_id.startswith('@'):
        user = User.query.filter(User.username.ilike(user_id[1:])).first()
    else:
        user = User.query.filter_by(id=id).first()

    # 404 if user not found
    if user is None:
        if wants_json_response(): return jsonify(error="User not found"), 404
        return render_user_template('errors/404_user.html'), 404

    # redirect to user page with id+username if not already
    if user_id != url_from_id(user.id, user.username):
        # /delete should not redirect
        if not request.url.endswith('/delete'):
            return redirect('/user/' + url_from_id(user.id, user.username))
    

    # return data if json response
    if wants_json_response(): return jsonify(user.to_dict())

    # implements delete functionality
    if request.method == 'DELETE' or request.url.endswith('/delete'):
       
        # check if user is authorized to delete
        auth_user = get_auth_user()
        if auth_user is None or not auth_user.admin and auth_user.id != user.id: 
            return jsonify(error="Unauthorized"), 401
        
        # delete all the user's collections
        for collection in user.collections:
            db.session.delete(collection)
            db.session.commit()

        # delete all the user's likes
        for like in user.likes:
            db.session.delete(like)
            db.session.commit()

        # delete user
        db.session.delete(user)
        db.session.commit()
        
        # return success
        if wants_json_response(): return jsonify(success=True), 200
        return redirect('/')

    # the groups of collections to display
    groups = {}

    # user collections
    if (len(user.collections) > 0):
        groups['collections'] = {
            'name': 'Collections',
            'items': reversed(user.collections),
            'link': False
        }

    # user likes
    if (len(user.likes) > 0):
        groups['likes'] = {
            'name': 'Likes',
            'items': reversed([like.collection for like in user.likes]),
            'link': False
        }

    # finally, render the user page
    return render_user_template("user.html", user=user, groups=groups)



