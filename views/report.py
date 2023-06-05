from views import main_blueprint as bp

# TODO: implement reporting

@bp.route('/collection/<collection_id>/report', methods=['POST', 'GET'])
def report_collection(collection_id):
    return 'Is this collection really worth reporting?'

@bp.route('/user/<user_id>/report', methods=['POST', 'GET'])
def report_user(user_id):
    return 'Is this user really worth reporting?'

@bp.route('/item/<item_id>/report-issues', methods=['POST', 'GET'])
def report_item_issue(item_id):
    return 'How dare you find an issue'
