from app.auth.models import User, History, Entry
from app.history.controllers import get_history_for_user
from flask import Flask, Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app.util.util import build_response_object, get_user_from_token
from app.api_paths import USER_BASE_URL

user_blueprint = Blueprint('user', __name__, url_prefix=USER_BASE_URL)

class UserHistoryAPI(MethodView):
    """ Returns a History object associated with an user """
    def get(self):
        #checa se usuário tem token válido
        auth_header = request.headers.get('Authorization')
        post_data = request.get_json()
        user, user_id = get_user_from_token(auth_header)
        #checa se usuário existe
        if(not(isinstance(user, User))):
            response = build_response_object('fail',USER_NOT_EXIST,"")
            return make_response(jsonify(response)), 404
        #recupera histórico para aquele usuário
        history = get_history_for_user(user)
        #se histórico nao existe, retorna erro
        if(not(isinstance(history, History))):
            response = build_response_object('fail', "", "")
            return make_response(jsonify(response)), 404
        #retorna historico
        history_obj = {
            "id": history.id,
            "name": history.name,
            "type": history.type,
            "user_id": history.user_id
        }
        response = build_response_object('success', history_obj, "")
        return make_response(jsonify(response)), 200

user_history_controller = UserHistoryAPI.as_view('user_history')

#rules for API endpoints
user_blueprint.add_url_rule(
    'history',
    view_func=user_history_controller,
    methods=['GET']
)
