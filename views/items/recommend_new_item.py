from views.items import item_bp


@item_bp.route('/item/recommend_new', methods=['GET', 'POST'])
def item_recommend():
    return 'item recommend route'

# TODO: Add a route for the item recommendation page
