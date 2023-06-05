import datetime
from flask import redirect, request, jsonify
from models import Collection, CollectionLike
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import get_form, wants_json_response
from views.collections import collection_bp
from app import db

@collection_bp.route('/collection/<collection_id>/like', methods=['POST'])
@collection_bp.route('/collection/<collection_id>/unlike', methods=['POST'])
def collection_like(collection_id):
    """
    New collection like 

    Allows users to like collections
    """

    # get user (if not logged in, redirect to login page)
    user = get_auth_user()
    if user is None:
        if wants_json_response(): return jsonify(error="Unauthorized"), 401
        return redirect('/login')
    
    # get collection (and error if not found)
    collection = Collection.query.filter_by(id=collection_id).first()
    if collection is None:
        return jsonify(error="Collection not found"), 404


    # get the action (like or unlike)
    if request.url.endswith('/like'):
        action = 'like'
    elif request.url.endswith('/unlike'):
        action = 'unlike'

    # check if user has already liked
    has_liked = collection.user_likes(user.id)

    # if the user wants to like the collection
    if action == 'like':
        # error if already liked
        if has_liked:
            if wants_json_response(): return jsonify(error="Already liked"), 400
            return redirect(collection.get_url_with_name())

        # create new collection like
        collection_like = CollectionLike(
            collection_id=collection.id,
            user_id=user.id,
            timestamp=datetime.datetime.utcnow(),
        )

        # save to db
        db.session.add(collection_like)
        db.session.commit()

    elif action == 'unlike':
        # error if not liked before
        if not has_liked:
            if wants_json_response(): return jsonify(error="Not liked"), 400
            return redirect(collection.get_url_with_name())

        # get the collection like
        collection_like = CollectionLike.query.filter_by(
            collection_id=collection.id,
            user_id=user.id,
        ).first()
        
        # delete from db
        db.session.delete(collection_like)
        db.session.commit()

    else:
        # error if invalid action (should never occur)
        return jsonify(error="Invalid action"), 400
    
    # return success or redirect back to the collections's page
    if wants_json_response(): return jsonify(success=True), 201
    return redirect(collection.get_url_with_name())





