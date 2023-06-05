from flask import request, jsonify
from tools.template import render_user_template
from models import Collection, Item
from views import main_blueprint as bp


@bp.route("/", methods=["GET", 'POST'])
def home():
    """
    Home page route
    """
    if request.method == 'POST':
        message = request.form['message']
        return jsonify(your_message=message)  

    # get all collections
    collections = Collection.query.all()

    # sort collections and get the top 10 (by age)
    new_collections = collections.copy()
    new_collections.sort(key=lambda x: x.created_timestamp, reverse=True)
    new_collections = new_collections[:10]

    # sort collections and get the top 10 (by likes)
    popular_collections = collections.copy()
    popular_collections.sort(key=lambda x: len(x.likes), reverse=True)
    popular_collections = popular_collections[:10]


    # get all items
    items = Item.query.all()

    # sort items and get the top 10 (by age)
    new_items = items.copy()
    new_items.sort(key=lambda x: x.created_timestamp, reverse=True)
    new_items = new_items[:10]

    # sort items and get the top 10 (by collections using them)
    popular_items = items.copy()
    popular_items.sort(key=lambda x: len(x.collections), reverse=True)
    popular_items = popular_items[:10]

    # group the collections and items (helpful for rendering)
    groups = {
        "popular-collections": {
            "name": "Popular Collections",
            "items": popular_collections,
            "link": "/collections/popular",
            "show_more": {
                "text": "Show More Collections",
                "link": "/collections/popular",
                "icon": "three-dots"
            },
        },
        "popular-items": {
            "name": "Popular Items",
            "items": popular_items,
            "link": "/items/popular",
            "show_more": {
                "text": "Show More Items",
                "link": "/items/popular",
                "icon": "three-dots"
            },
        },
        "new-collections": {
            "name": "New Collections",
            "items": new_collections,
            "link": "/collections/recent",
            "show_more": {
                "text": "Show More Collections",
                "link": "/collections/recent",
                "icon": "three-dots"
            },
        },
        "new-items": {
            "name": "New Items",
            "items": new_items,
            "link": "/items/recent",
            "show_more": {
                "text": "Show More Items",
                "link": "/items/recent",
                "icon": "three-dots"
            },
        },
    }

    # get the items for the carousel on homepage
    carousel_items = []

    # top 5 collections and items (interlaced)
    for i in range(5):
        if len(popular_collections) > i: carousel_items.append(popular_collections[i])
        if len(popular_items) > i: carousel_items.append(popular_items[i])

    # finally, render the template
    return render_user_template(
        "index.html", 
        groups=groups, 
        carousel_items=carousel_items,
        main_type='home'
    )


