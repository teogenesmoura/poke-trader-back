from app.auth.models import User, History, Entry
from flask import Flask, Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app.extensions import bcrypt,db
from app.util.util import build_response_object, get_user_from_token
from app.messages import RESOURCE_CREATION_SUCCESS, USER_NOT_EXIST, INVALID_USER_ID, NO_DATA_FOUND, \
                         INCOMPLETE_DATA, INVALID_TOKEN, GENERIC_ERROR
from app.api_paths import HISTORY_BASE_URL
history_blueprint = Blueprint('history', __name__, url_prefix=HISTORY_BASE_URL)

def get_history_for_user(user):
    history = ''
    try:
        history = History.query.filter_by(
            user_id=user.id
        ).first()
    except Exception as e:
        return e
    return history

@history_blueprint.before_request
def check_data_presence_before_route():
    data = request.get_json()
    if not data:
        resp = build_response_object('fail', NO_DATA_FOUND, "")
        return make_response(jsonify(resp)), 400

class HistoryAPI(MethodView):
    def post(self):
        auth_header = request.headers.get('Authorization')
        user, user_id = get_user_from_token(auth_header)
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

class SingleEntryAPI(MethodView):
    """ Handles requests for a single Entry object """
    def post(self):
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

entry_controller = SingleEntryAPI.as_view('entry')

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

history_controller = HistoryAPI.as_view('history')
history_entries_controller = EntriesAPI.as_view('entries')

#rules for API endpoints
history_blueprint.add_url_rule(
    "/",
    view_func=history_controller,
    methods=['POST']
)
history_blueprint.add_url_rule(
    "/<history_id>",
    view_func=history_controller,
    methods=['GET']
)
history_blueprint.add_url_rule(
    "/<history_id>/entries",
    view_func=history_entries_controller,
    methods=['GET']
)
