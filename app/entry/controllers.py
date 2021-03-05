import json
from app.auth.models import User, Entry
from flask import Flask, Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app.extensions import bcrypt,db
from app.util.util import build_response_object, get_user_from_token
from app.messages import RESOURCE_CREATION_SUCCESS, USER_NOT_EXIST, INVALID_USER_ID, NO_DATA_FOUND, \
                         INCOMPLETE_DATA, INVALID_TOKEN, GENERIC_ERROR
from app.api_paths import ENTRY_BASE_URL
entry_blueprint = Blueprint('entry', __name__)

class SingleEntryAPI(MethodView):
    """ Handles requests for a single Entry object """
    def post(self):
        #checa se usuário tem token válido
        auth_header = request.headers.get('Authorization')
        post_data = request.get_json()
        print("post_data")
        print(post_data)
        user, user_id = get_user_from_token(auth_header)
        #checa se usuário existe
        if(not(isinstance(user, User))):
            response = build_response_object('fail',USER_NOT_EXIST,"")
            return make_response(jsonify(response)), 404
        #insere entry no histórico
        host = json.dumps(post_data.get('host'))
        opponent = json.dumps(post_data.get('opponent'))
        simulation_successfull=post_data.get('simulation_successfull')
        print("type simulation_successfull")
        print(type(simulation_successfull))
        entry_info = {}
        if host and opponent:
            try:
                entry = Entry(
                    host=host,
                    opponent=opponent,
                    user_id=user_id,
                    simulation_successfull=simulation_successfull
                )
                db.session.add(entry)
                db.session.commit()
                entry_info = {
                    'host': entry.host,
                    'opponent': entry.opponent,
                    'simulation_successfull': entry.simulation_successfull
                }
            except Exception as error:
                print(error)
                response = build_response_object('fail', GENERIC_ERROR, "")
                return make_response(jsonify(response)), 500
        response = build_response_object('success', entry_info, "")
        return make_response(jsonify(response)), 200

class EntriesAPI(MethodView):
    """ Returns all Entry objects associated with a User object """
    def get(self):
        #checa se usuário tem token válido
        auth_header = request.headers.get('Authorization')
        post_data = request.get_json()
        user, user_id = get_user_from_token(auth_header)
        #checa se usuário existe
        if(not(isinstance(user, User))):
            response = build_response_object('fail',USER_NOT_EXIST,"")
            return make_response(jsonify(response)), 404
        try:
            entries = Entry.query.filter_by(user_id=user_id).all()
        except Exception as error:
            response = build_response_object('fail', GENERIC_ERROR, "")
            return make_response(jsonify(response)), 500
        if not entries:
            entries = "No entries found"
        response = build_response_object('success', entries, "")
        return make_response(jsonify(response)), 200

entry_controller = SingleEntryAPI.as_view('entry')
entries_controller = EntriesAPI.as_view('entries')

#rules for API endpoints
entry_blueprint.add_url_rule(
    '/user/entry',
    view_func=entry_controller,
    methods=['POST']
)
entry_blueprint.add_url_rule(
    "/user/entries",
    view_func=entries_controller,
    methods=['GET']
)
