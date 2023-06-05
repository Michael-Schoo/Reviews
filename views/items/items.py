from datetime import datetime, timedelta
from flask import jsonify, redirect
from models import Item
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import wants_json_response
from views.items import item_bp
from views.items.new_item import item_new

old_date = datetime(year=2000, month=1, day=1) 



@item_bp.route('/items', methods=['GET'])
def items():
    """
    Items route
    """

    items: list[Item] = Item.query.all()

    # return json if wants json from accept header
    if wants_json_response():
        return jsonify([item.to_dict() for item in items])
    
    # make groups of items by type and other things
    # one for popular (most used in collections)
    # one for recently added
    # one for each type (movie, book, song, etc.)
    groups = {
        "popular": {
            "name": "Popular Items",
            "items": items.copy(),
            "link": "/items/popular",
        },
        "movie": {
            "name": "Movies",
            "items": [],
            "show_more": {
                "text": "Show More Movies",
                "link": "/items/movie",
                "icon": "three-dots"
            },
            "link": "/items/movie",
        },
        "book": {
            "name": "Books",
            "items": [],
            "show_more": {
                "text": "Show More Books",
                "link": "/items/book",
                "icon": "three-dots"
            },
            "link": "/items/book"
        },
        "song": {
            "name": "Songs",
            "items": [],
            "show_more": {
                "text": "Show More Songs",
                "link": "/items/song",
                "icon": "three-dots"
            },
            "link": "/items/song",
        },
        "recent": {
            "name": "Recently Added Items",
            "items": [],
            "link": "/items/recent",
        },
    }

    # add each item to its group
    for item in items:
        groups[item.type]['items'].append(item)

    # sort each item by date and get the last 10
    for key in ['movie', 'book', 'song']:
        groups[key]['items'].sort(key=lambda item: item.updated_timestamp or old_date, reverse=True)
        groups[key]['items'] = groups[key]['items'][:10]

    # sort by most used in collections
    groups["popular"]['items'].sort(key=lambda item: len(item.collections), reverse=True)
    groups["popular"]['items'] = groups["popular"]['items'][:10]

    # sort by most recently added
    # filter out items not new in one month 
    groups["recent"]['items'] = list(filter(lambda item: (item.created_timestamp or old_date) > datetime.utcnow() - timedelta(days=30), items))
    groups["recent"]['items'].sort(key=lambda item: item.created_timestamp or datetime(year=2000, month=1, day=1), reverse=True)
    groups["recent"]['items'] = groups["recent"]['items'][:10]

    # if there no recent items, remove the group
    if (not len(groups["recent"]['items'])):
        del groups["recent"]

    # finally, render the template
    return render_user_template(
        "items.html", 
        groups=groups, 
        main_type='item'
    )

@item_bp.route('/items/<type>', methods=['GET'])
def items_type(type):
    """
    similar to above but instead of a few of each, it is all of one type
    """

    # The new item route is at has its own function
    if type == 'new': return item_new()

    # currently popular and recent are the same as all
    if type in ['popular', 'recent']:
        return redirect('/items/all')
    
    # make a dict of the names of each type
    groups_names = {
        "movie": "Movies",
        "book": "Books",
        "song": "Songs",
        "all": "All Items",
    }

    # add the respective items to the items list
    items: list[Item] = []
    if type == 'all':
        items = Item.query.all()
    else:
        items = Item.query.filter_by(type=type).all()

    # if wants json from accept header
    if wants_json_response():
        return jsonify([item.to_dict() for item in items])
        
    # make the info data for the template
    info_data = {
        "sub_name": groups_names[type],
        "main_name": "Items",
        "main_id": "items",
    }

    # gets the current user (to show the ability to make new items if admin)
    current_user = get_auth_user()

    if current_user and current_user.admin:
        info_data["make_new"] = {
            "text": "Make New Item",
            "short_text": "New Item",
            "link": f"/items/new?type={type}" if type != 'all' else '/items/new',
        }
    
    # render the template
    return render_user_template(
        "items_grouped.html", 
        items=items, 
        info_data = info_data
    )