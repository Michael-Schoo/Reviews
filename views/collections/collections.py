from flask import redirect, request, jsonify
from sqlalchemy import or_
from models import Collection
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import wants_json_response
from views.collections import collection_bp
from views.collections.new_collection import collection_new
from datetime import datetime, timedelta
from flask import jsonify, redirect
from models import Item
from tools.template import render_user_template
from tools.tools import wants_json_response
from views.items import item_bp
from views.items.new_item import item_new

old_date = datetime(year=2000, month=1, day=1) 


# /collections redirects to /collections (a common mistake for users)
@collection_bp.route('/collection', methods=['GET'])
def collection(): return redirect('/collections')


@item_bp.route('/collections', methods=['GET'])
def collections():
    """
    Collections route
    """

    collections: list[Collection] = Collection.query.all()

    # return json if wants json from accept header
    if wants_json_response():
        return jsonify([item.to_dict() for item in collections])
    
    # make groups of collections by popularity and recency
    # popular is most liked
    # recent is most recently updated
    groups = {
        "popular": {
            "name": "Popular Collections",
            "items": collections.copy(),
            "link": "/collections/popular",
            "show_more": {
                "text": "Show More Collections",
                "link": "/collections/popular",
                "icon": "three-dots"
            },
        },
        "recent": {
            "name": "Recently Made Collections",
            "items": [],
            "link": "/collections/recent",
        },
    }

    #TODO: Add tag support

    # sort popular by number of stars (most first)
    groups["popular"]['items'].sort(key=lambda collection: collection.get_number_of_likes(), reverse=True)
    groups["popular"]['items'] = groups["popular"]['items'][:10]

    # sort recent by date updated (most recent first)
    groups["recent"]['items'] = collections.copy()
    groups["recent"]['items'].sort(key=lambda collection: collection.updated_timestamp or old_date, reverse=True)
    groups["recent"]['items'] = groups["recent"]['items'][:10]

    # if user, show their collections
    current_user = get_auth_user()
    if current_user:
        groups["collections"] = {
            "name": "Your Collections",
            "items": current_user.collections,
            "link": False,
        }

    # finally, render the template
    return render_user_template(
        "collections.html", 
        groups=groups, 
        main_type='collection'
    )

@item_bp.route('/collections/<type>', methods=['GET'])
def collections_type(type):
    """
    similar to above but instead of a few of each, it is all of one type
    """

    # The new item route is at has its own function
    if type == 'new': return collection_new()

    # currently popular and recent are the same as all
    if type in ['popular', 'recent']:
        return redirect('/collections/all')

    # make a dict of the names of each type
    groups_names = {
        "all": "All Collections",
    }

    # add the respective collections to the items list
    items: list[Collection] = []
    if type == 'all':
        items = Collection.query.all()
    else:
        items = Collection.query.filter_by(type=type).all()

    # if wants json from accept header
    if wants_json_response():
        return jsonify([item.to_dict() for item in items])
    
    # make the info data for the template
    info_data = {
        "sub_name": groups_names[type],
        "main_name": "Collections",
        "main_id": "collection",
        "make_new": {
            "text": "Make New Collection",
            "short_text": "New Collection",
            "link": f"/collections/new?type={type}" if type != 'all' else '/collections/new',
        },
    }

    # render the template
    return render_user_template(
        "items_grouped.html", 
        items=items, 
        info_data = info_data
        )

