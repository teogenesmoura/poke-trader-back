from app.auth.models import User, History
from flask import Flask, Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app.extensions import bcrypt,db
from app.util.util import build_response_object
from app.messages import RESOURCE_CREATION_SUCCESS, USER_NOT_EXIST, INVALID_USER_ID, NO_DATA_FOUND, \
                         INCOMPLETE_DATA, INVALID_TOKEN, GENERIC_ERROR
from app.api_paths import HISTORY_BASE_URL
history_blueprint = Blueprint('history', __name__)

@history_blueprint.before_request
def check_data_presence_before_route():
    data = request.get_json()
    if not data:
        resp = build_response_object('fail', NO_DATA_FOUND, "")
        return make_response(jsonify(resp)), 400

class HistoryAPI(MethodView):
    def get_user_from_token(self,auth_header):
        user = False
        auth_token = auth_header.split(" ")[1] if auth_header else ''
        if auth_token:
            user_id = User.decode_auth_token(auth_token)
            user = User.query.filter_by(id=user_id).first()
        if not user:
            resp = build_response_object('fail', USER_NOT_EXIST, "")
            return make_response(jsonify(resp)), 406
        return user, user_id

    def post(self):
        auth_header = request.headers.get('Authorization')
        user, user_id = self.get_user_from_token(auth_header)
        post_data = request.get_json()
        name = post_data.get('name')
        type = post_data.get('type')
        if not name or not type:
            resp = build_response_object('fail', INCOMPLETE_DATA, "")
            return make_response(jsonify(resp)), 400
        try:
            history = History(
                name=name,
                type=type,
                user_id=user_id
            )
            db.session.add(history)
            db.session.commit()
        except Exception as error:
            resp = build_response_object('fail', GENERIC_ERROR, "")
            return make_response(jsonify(resp)), 500
        message = { "resource_uri": HISTORY_BASE_URL + str(history.id) }
        resp = build_response_object('success', message, "")
        return make_response(jsonify(resp)), 201

    def get(self, history_id):
        try:
            history = History.query.filter_by(id=history_id).first()
        except Exception as error:
            resp = build_response_object('fail', GENERIC_ERROR, "")
            return make_response(jsonify(resp)), 500
        return jsonify(history)


history_controller = HistoryAPI.as_view('history')

#rules for API endpoints
history_blueprint.add_url_rule(
    HISTORY_BASE_URL,
    view_func=history_controller,
    methods=['POST']
)
history_blueprint.add_url_rule(
    HISTORY_BASE_URL + "/<history_id>",
    view_func=history_controller,
    methods=['GET']
)
