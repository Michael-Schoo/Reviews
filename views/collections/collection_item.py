import datetime
from flask import redirect, request, jsonify
from models import Collection, CollectionItem, Item
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import get_form, id_from_url, url_from_id, wants_json_response
from views.collections import collection_bp
from app import db


@collection_bp.route('/collection/<collection_id>/item/<item_id>', methods=['GET', 'POST', 'DELETE'])
@collection_bp.route('/collection/<collection_id>/item/<item_id>/delete', methods=['POST'])
@collection_bp.route('/item/<item_id>/add-to-collection', methods=['POST'], defaults={'collection_id': None})
def collection_item(collection_id, item_id):

    if collection_id is None:
        # allow /item/<item_id>/add-to-collection
        collection_id = request.form.get('collection_id')
        
        # but if it is still None, then error
        if collection_id is None:
            return jsonify(error="Invalid request"), 400
        

    # check collection exists
    collection = Collection.query.filter_by(id=collection_id).first()
    
    # if collection not found, return error
    if collection is None: return jsonify(error="Collection not found"), 404

    # if item in collection, return true
    if request.method == 'GET':
        return jsonify(exists='true')


    # check if user is logged in and is admin/owner of collection
    user = get_auth_user()
    if user is None: return jsonify(error="Unauthorized"), 401
    if (collection.user_id != user.id) and not user.admin: return jsonify(error="Forbidden"), 403

    # check if item exists and error if not
    item = Item.query.filter_by(id=item_id).first()
    if item is None:
        return jsonify(error="Item not found"), 404
    
    # for adding item to collection
    if request.method == 'POST':
            
        # currently no duplicate items allowed in collection
        if item in collection.items:
            return jsonify(error="Item already in collection"), 400

        # add item to collection 
        collection_item = CollectionItem(
            collection_id=collection.id,
            item_id=item.id,
            added_timestamp=datetime.datetime.utcnow(),
        )
        db.session.add(collection_item)

        # update collection timestamp
        db.session.commit()

        # redirect to main collection page or return success
        if wants_json_response(): return jsonify(success=True)
        return redirect(collection.get_url_with_name())
    
    # for removing item from collection
    if request.method == 'DELETE' or request.url.endswith('/delete'):
        # check if item is in collection (needs to exist to delete)
        collection_item = CollectionItem.query.filter_by(collection_id=collection.id, item_id=item.id).first()
        if collection_item is None:
            return jsonify(error="Item not in collection"), 400
       
        # remove item from collection
        db.session.delete(collection_item)

        # update collection timestamp
        collection.updated_timestamp = datetime.datetime.utcnow()
        db.session.commit()

        # redirect to main collection page or return success
        if wants_json_response(): return jsonify(success=True)
        return redirect(collection.get_url_with_name())
    
    # should never get here
    return jsonify(error="Invalid request"), 400
    