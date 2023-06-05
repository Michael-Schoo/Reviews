import datetime
from flask import redirect, request, jsonify
from models import Collection, CollectionComment, Item, ItemComment
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import get_form, id_from_url, url_from_id, wants_json_response
from . import main_blueprint as bp
from app import db


@bp.route('/item/<item_id>/comments', methods=['GET'], defaults={'collection_id': None})
@bp.route('/collection/<collection_id>/comments', methods=['GET'], defaults={'item_id': None})
def comments_page(item_id: str | None, collection_id: str | None):
    """
    Comments page route

    this is for getting all the comments for an item or collection
    """

    # get user
    user = get_auth_user()
    if user is None: return jsonify(error="Unauthorized"), 401

    # get item
    if item_id:
        item = Item.query.get(item_id)
        if item is None: return jsonify(error="Item not found"), 404

        return jsonify([comment.to_dict() for comment in item.comments])
        
    
    elif collection_id:
        collection = Collection.query.get(collection_id)
        if collection is None: return jsonify(error="Collection not found"), 404

        return jsonify([comment.to_dict() for comment in collection.comments])
        

@bp.route('/item/<item_id>/comment', methods=['POST'], defaults={'collection_id': None})
@bp.route('/collection/<collection_id>/comment', methods=['POST'], defaults={'item_id': None})
def comments(item_id: str | None, collection_id: str | None):
    """
    Comments route

    this is for adding a comment to an item or collection
    """


    # get user
    user = get_auth_user()
    if user is None: return jsonify(error="Unauthorized"), 401

    data = get_form()
    comment = data.get('comment')

    # if the comment is for an item
    if item_id:
        # try to get the item (if it doesn't exist, return 404)
        item = Item.query.get(item_id)
        if item is None: return jsonify(error="Item not found"), 404

        # create the comment
        new_comment = ItemComment(
            user_id=user.id, 
            item_id=item.id, 
            comment=comment,
            timestamp=datetime.datetime.utcnow(),
        )

        # add the comment to the database
        db.session.add(new_comment)
        db.session.commit()

        # return the comment or redirect to the item page
        if wants_json_response(): return jsonify(new_comment.to_dict())
        return redirect('/item/' + url_from_id(item.id, item.name))
    
    # if the comment is for a collection
    elif collection_id:
        # try to get the collection (if it doesn't exist, return 404)
        collection = Collection.query.get(collection_id)
        if collection is None: return jsonify(error="Collection not found"), 404

        # create the comment
        new_comment = CollectionComment(
            user_id=user.id,
            collection_id=collection.id,
            comment=comment,
            timestamp=datetime.datetime.utcnow(),
        )

        # add the comment to the database
        db.session.add(new_comment)
        db.session.commit()

        # return the comment or redirect to the collection page
        if wants_json_response(): return jsonify(new_comment.to_dict())
        return redirect('/collection/' + url_from_id(collection.id, collection.name))
    
    else:
        # should never happen
        return jsonify(error="Bad request"), 400
    

# get/update/remove comment
@bp.route('/item/<item_id>/comment/<comment_id>', methods=['GET', 'PATCH', 'DELETE'], defaults={'collection_id': None})
@bp.route('/collection/<collection_id>/comment/<comment_id>', methods=['GET', 'PATCH', 'DELETE'], defaults={'item_id': None})
def comment_page(item_id: str | None, collection_id: str | None, comment_id: str):
    """
    Comment page route

    this is for getting, updating, or removing a comment
    """
    
    # sets the variables
    comment = None
    item = None
    collection = None

    # get item
    if item_id:
        item = Item.query.get(item_id)
        if item is None: return jsonify(error="Item not found"), 404

        comment = ItemComment.query.get(comment_id)

    #  or get collection
    elif collection_id:
        collection = Collection.query.get(collection_id)
        if collection is None: return jsonify(error="Collection not found"), 404

        comment = CollectionComment.query.get(comment_id)

    # if the comment doesn't exist, return 404
    if comment is None: return jsonify(error="Comment not found"), 404

    # if the request is a GET, return the comment
    if request.method == 'GET':
        if wants_json_response(): return jsonify(comment.to_dict())
        return redirect('/item/' + url_from_id(item.id, item.name))
    
    # get user (if they don't exist, return 401)
    user = get_auth_user()
    if user is None: return jsonify(error="Unauthorized"), 401

    # user has to either be the owner of the collection or the owner of the comment or user is admin
    if user.id != comment.user_id and user.id != collection.user_id and not user.admin:
        return jsonify(error="Unauthorized"), 401
    
    # if the request is a PATCH, update the comment
    if request.method == 'PATCH':

        # get data from form and update the comment
        data = get_form()
        comment.comment = data.get('comment')
        db.session.commit()

        # return the comment or redirect to the item page
        if wants_json_response(): return jsonify(comment.to_dict())
        return redirect('/item/' + url_from_id(item.id, item.name))
    
    elif request.method == 'DELETE':
        # delete the comment
        db.session.delete(comment)
        db.session.commit()

        # return the success or redirect to the item page
        if wants_json_response(): return jsonify(success=True)
        return redirect('/item/' + url_from_id(item.id, item.name))
    
    # should never happen
    return jsonify(error="Bad request"), 400
