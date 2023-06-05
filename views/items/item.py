import datetime
from flask import redirect, request, jsonify
from models import CollectionItem, Item
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import get_form, id_from_url, url_from_id, wants_json_response
from views.items import item_bp
from app import db

@item_bp.route('/item/<item_id>', methods=['GET', 'PATCH', 'DELETE'])
@item_bp.route('/item/<item_id>/edit', methods=['POST'])
@item_bp.route('/item/<item_id>/delete', methods=['POST'])

def item_page(item_id):
    """
    Item page route
    """

    # get the item id (because can be `2-the-hunger-games` and we only want the id)
    actual_item_id = id_from_url(item_id)

    # find the item
    item: Item = Item.query.get(actual_item_id)

    # error if item not found
    if not item:
        if wants_json_response(): return jsonify(error="Item not found"), 404
        return render_user_template('errors/404_item.html'), 404

    # redirect if url doesn't use the fancy url method (e.g. /item/2-the-hunger-games)
    if item_id != url_from_id(actual_item_id, item.name):
        # /edit and /delete are allowed (no need to redirect)
        if request.url.endswith('/edit') or request.url.endswith('/delete'):
            pass
        else:
            return redirect(item.get_url_with_name())
    
    # gets the user (because need to check if they can edit/delete)
    user = get_auth_user()

    # return the item page (or json data)
    if request.method == 'GET':
        if wants_json_response(): return jsonify(item.to_dict())
        return render_user_template("item.html", item=item)

    # for editing
    if request.method == 'PATCH' or request.url.endswith('/edit'):
        # check if user is logged in and is admin
        if user is None: return jsonify(error="Unauthorized"), 401
        if not user.admin: return jsonify(error="Forbidden"), 403
        
        # get the form data
        data = get_form()
        name = data.get('name')
        description = data.get('description')
        image_url = data.get('image-url')

        # only modify provided data
        if name: item.name = name
        if description: item.description = description
        if image_url: item.image_url = image_url

        # change the extra data depending on the type of item
        if item.type == 'movie':
            # change movie data
            director = data.get('director')
            year = data.get('year')
            length = data.get('length')

            if director: item.movie.director = director
            if year: item.movie.year = year
            if length: item.movie.length = length

        elif item.type == 'book':
            # change book data
            author = data.get('author')
            year = data.get('year')
            country = data.get('country')
            language = data.get('language')

            if author: item.book.author = author
            if year: item.book.year = year
            if country: item.book.country = country
            if language: item.book.language = language

        elif item.type == 'song':
            # change song data
            artist = data.get('artist')
            year = data.get('year')
            length = data.get('length')

            if artist: item.song.artist = artist
            if year: item.song.year = year
            if length: item.song.length = length
                        
        # update the timestamp
        item.updated_timestamp = datetime.datetime.utcnow()

        # save the changes
        db.session.commit()
        
        # return success or redirect back to the item's page
        if wants_json_response(): return jsonify(success=True)
        return redirect(item.get_url_with_name())

    
    if request.method == 'DELETE' or request.url.endswith('/delete'):
        # check if user is logged in and is admin
        if user is None: return jsonify(error="Unauthorized"), 401
        if not user.admin: return jsonify(error="Forbidden"), 403

        # go through each collection, and remove item from it
        collections = CollectionItem.query.filter_by(item_id=item.id).all()
        for collection in collections:
            db.session.delete(collection)

        # delete the extra data depending on the type of item
        if item.type == 'movie':
            db.session.delete(item.movie)
        elif item.type == 'book':
            db.session.delete(item.book)
        elif item.type == 'song':
            db.session.delete(item.song)

        # delete the item's comments
        for comment in item.comments:
            db.session.delete(comment)

        # delete the item
        db.session.delete(item)

        # save the changes
        db.session.commit()
        
        # return success or redirect back to the home page
        if wants_json_response(): return jsonify(success=True)
        return redirect('/')
