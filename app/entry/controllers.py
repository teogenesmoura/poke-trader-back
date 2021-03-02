import json
from app.auth.models import User, Entry, History
from flask import Flask, Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app.extensions import bcrypt,db
from app.history.controllers import get_history_for_user
from app.util.util import build_response_object, get_user_from_token
from app.messages import RESOURCE_CREATION_SUCCESS, USER_NOT_EXIST, INVALID_USER_ID, NO_DATA_FOUND, \
                         INCOMPLETE_DATA, INVALID_TOKEN, GENERIC_ERROR
from app.api_paths import ENTRY_BASE_URL
entry_blueprint = Blueprint('entry', __name__)

class SingleEntryAPI(MethodView):
    """ Handles requests for a single Entry object """
    def post(self, history_id):
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
            response = build_response_object('fail', HISTORY_NOT_EXIST, "")
            return make_response(jsonify(response)), 404
        #insere entry no histórico
        host = json.dumps(post_data.get('host'))
        opponent = json.dumps(post_data.get('opponent'))
        history_id = post_data.get('history_id')
        if host and opponent:
            try:
                entry = Entry(
                    host=host,
                    opponent=opponent,
                    history_id=history_id
                )
                db.session.add(entry)
                db.session.commit()
                entry_info = {
                    'host': entry.host,
                    'opponent': entry.opponent,
                    'history_id': entry.history_id
                }
            except Exception as error:
                response = build_response_object('fail', GENERIC_ERROR, "")
                return make_response(jsonify(response)), 500
        response = build_response_object('success', entry_info, "")
        return make_response(jsonify(response)), 200

class EntriesAPI(MethodView):
    """ Returns all Entry objects associated with a History object """
    def get(self, history_id):
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
            response = build_response_object('fail', HISTORY_NOT_EXIST, "")
            return make_response(jsonify(response)), 404
        #recupera entries para o histórico
        try:
            entries = Entry.query.filter_by(history_id=history_id).all()
        except Exception as error:
            print(error)
            return "deu erro"
        response = build_response_object('success', entries, "")
        return make_response(jsonify(response)), 200

entry_controller = SingleEntryAPI.as_view('entry')
entries_controller = EntriesAPI.as_view('entries')

#rules for API endpoints
entry_blueprint.add_url_rule(
    '/history/<history_id>/entry',
    view_func=entry_controller,
    methods=['POST']
)
entry_blueprint.add_url_rule(
    "/history/<history_id>/entries",
    view_func=entries_controller,
    methods=['GET']
)
