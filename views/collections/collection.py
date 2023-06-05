import datetime
from flask import redirect, request, jsonify
from models import Collection, CollectionItem
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import get_form, id_from_url, url_from_id, wants_json_response
from views.collections import collection_bp
from app import db


@collection_bp.route('/collection/<collection_id>', methods=['GET', 'PATCH', 'DELETE'])
@collection_bp.route('/collection/<collection_id>/edit', methods=['POST'])
@collection_bp.route('/collection/<collection_id>/delete', methods=['POST'])
def collection_page(collection_id):
    """
    Collection page route
    """

    # get the item id (because can be `2-the-best-movies` and we only want the id)
    actual_collection_id = id_from_url(collection_id)

    # find the collection
    collection: Collection = Collection.query.filter_by(id=actual_collection_id).first()

    # error if collection not found
    if not collection:
        if wants_json_response(): return jsonify(error="collection not found"), 404
        return render_user_template('errors/404_collection.html'), 404
    
    # gets the user (because they needed to be logged in to create a collection)
    user = get_auth_user()
    
    # redirect if url doesn't use the fancy url method (e.g. /collection/2-the-best-movies)
    if collection_id != url_from_id(actual_collection_id, collection.name):
        # /edit and /delete are allowed (no need to redirect)
        if request.url.endswith('/edit') or request.url.endswith('/delete'):
            pass
        else:
            return redirect(collection.get_url_with_name())
    
    # return the collection page (or json data)
    if request.method == 'GET':
        if wants_json_response(): return jsonify(collection.to_dict())
        return render_user_template("collection.html", collection=collection)

    # for editing
    if request.method == 'PATCH' or request.url.endswith('/edit'):
        # check if user is logged in and is admin/owner of collection
        if user is None: return jsonify(error="Unauthorized"), 401
        if (collection.user_id != user.id) and not user.admin: return jsonify(error="Forbidden"), 403
        
        # get the form data
        data = get_form()
        name = data.get('name')
        description = data.get('description')

        # only modify provided data
        if name: collection.name = name
        if description: collection.description = description

        # update the timestamp
        collection.updated_timestamp = datetime.datetime.utcnow()

        # save the changes
        db.session.commit()

        # return success or redirect back to the item's page
        if wants_json_response(): return jsonify(success=True)
        return redirect('/collection/' + str(collection.id))

    if request.method == 'DELETE' or request.url.endswith('/delete'):
        # check if user is logged in and is admin/owner of collection
        if user is None: return jsonify(error="Unauthorized"), 401
        if (collection.user_id != user.id) and not user.admin: return jsonify(error="Forbidden"), 403

        # remove all items in collection
        collections = CollectionItem.query.filter_by(collection_id=collection.id).all()
        for collection in collections:
            db.session.delete(collection)

        # delete the collection's comments
        for comment in collection.comments:
            db.session.delete(comment)

        # delete the collection
        db.session.delete(collection)

        # save the changes
        db.session.commit()

       
        # return success or redirect back to the home page
        if wants_json_response(): return jsonify(success=True)
        return redirect('/')
    

