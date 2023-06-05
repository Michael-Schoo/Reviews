import datetime
from flask import redirect, jsonify
from models import Collection, CollectionItem
from tools.jwt_token import get_auth_user
from tools.tools import get_form
from views.collections import collection_bp
from app import db


@collection_bp.route('/collection/<collection_id>/fork', methods=['POST'])
def collection_fork(collection_id):
    """
    Fork collection route
    """

    # get user (if not logged in, throw error)
    user = get_auth_user()
    if user is None:
        return jsonify(error="Unauthorized"), 401

    # get collection (and error if not found)
    collection = Collection.query.filter_by(id=collection_id).first()
    if collection is None:
        return jsonify(error="Collection not found"), 404
    
    # create the collection
    new_collection = Collection(
        name = collection.name, 
        description = collection.description, 
        user_id= user.id, 
        forked_from_id=collection.id,
        created_timestamp=datetime.datetime.utcnow(),
        updated_timestamp=datetime.datetime.utcnow(),
        is_fork=True
    )

    # add the collection to the database
    db.session.add(new_collection)
    db.session.commit()

    # now add all the items (copy them)
    for item in collection.items:
        collection_item = CollectionItem(
            collection_id=new_collection.id,
            item_id=item.id,
            added_timestamp=datetime.datetime.utcnow(), 
        )
        # add those also to db
        db.session.add(collection_item)
        db.session.commit()

    # redirect to the collection page (with the edit modal)
    return redirect(new_collection.get_url_with_name()+'#edit')

