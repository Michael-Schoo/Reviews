import datetime
from flask import redirect, request, jsonify
from models import Collection
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import get_form, wants_json_response
from views.collections import collection_bp
from app import db

@collection_bp.route('/collection', methods=['POST'])
@collection_bp.route('/collection/new', methods=['GET'])
def collection_new():
    """
    New collection route

    Allows users to create new collections
    """

    # get user (if not logged in, redirect to login page)
    user = get_auth_user()
    if user is None:
        if wants_json_response(): return jsonify(error="Unauthorized"), 401
        return redirect('/login')
    
    # if GET then show the form
    if request.method == 'GET':
        return render_user_template("collection_new.html")

    # if POST, then create item
    if request.method == 'POST':
        # get the form data
        data = get_form()
        name = data.get('name')
        description = data.get('description')

        # Check if name is valid
        if not name and not description: 
            return jsonify(error="Invalid name", reason="Name and description is required"), 400

        # Create collection
        collection = Collection(
            name=name, 
            description=description, 
            user_id=user.id, 
            created_timestamp=datetime.datetime.utcnow(),
            updated_timestamp=datetime.datetime.utcnow(),
        )

        # add the collection to the database
        db.session.add(collection)
        db.session.commit()

        # return the new data by redirecting
        return redirect(collection.get_url_with_name())

