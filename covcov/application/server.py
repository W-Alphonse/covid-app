import datetime

from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS

from covcov.infrastructure.configuration import config

from covcov.application import route_dispatcher

# Flask object and properties
from covcov.infrastructure.db.database import Database
from covcov.infrastructure.cognito.idp_connexion import IdpConnexion

app = Flask(__name__)
PORT = config["api"]["port"]
HOST = config["api"]["host"]
#
#CORS(app)
CORS(app, supports_credentials=True)
#app.config['CORS_HEADERS'] = 'Content-Type'

db = Database("database")
region         = config["cognito"]["COG_REGION"]
user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]
app_client_id  = config["cognito"]["COG_APP_CLIENT_ID"]
cognito_idp = IdpConnexion(region, user_pool_id, app_client_id)
#
payload_as_lambda = True
BODY    = "body"

@app.route("/company_domain", methods=["POST"])
@cross_origin(headers=['Content-Type'])
def subscription_api():
    return _process_result( route_dispatcher.dispatch(request.get_json(), request.args, cognito_idp.get_claims(request.headers['auth-id-token'],'id'), request.path, db) )

def _process_result(result:dict) :
    return result[BODY]  if payload_as_lambda else jsonify(result)

@app.route("/visit_domain", methods=["POST"])
@cross_origin(headers=['Content-Type'])
def visit_api():
    return _process_result(route_dispatcher.dispatch(request.get_json(), request.args, None, request.path, db))

@app.route("/c_ccontact", methods=["POST"])
@cross_origin(headers=['Content-Type'])
def c_ccontact_api():
    return _process_result(route_dispatcher.dispatch(request.get_json(), request.args, cognito_idp.get_claims(request.headers['auth-id-token'],'id'), request.path, db))
    # return _process_result(route_dispatcher.dispatch(request.get_json(), request.args, {'sub':'82efcde5-84f1-403f-b6ad-0af5cd98a7c3'}, request.path, db))

@app.route("/a_ccontact", methods=["POST"])
@cross_origin(headers=['Content-Type'])
def a_ccontact_api():
    return _process_result(route_dispatcher.dispatch(request.get_json(), request.args, cognito_idp.get_claims(request.headers['auth-id-token'],'id'), request.path, db))

@app.route("/example", methods=["POST"])
def example():
    try:
        g = request.args
        print(f"Type:{type(g)} - Question:{g['question']}")
        initial_number = request.get_json()["question"]
        answer = float(initial_number)*2
    except (ValueError, TypeError, KeyError):
        DEFAULT_RESPONSE = 0
        answer = DEFAULT_RESPONSE
    response = {"answer": answer}
    return jsonify(response)

@app.route("/echo", methods=["GET"])
@cross_origin(headers=['Content-Type'])
def echo():
    return jsonify({"echo":"hello"})


# @app.before_first_request
# def before_start():
#     db.create_tables()

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()

if __name__ == "__main__":
    print("starting API at", datetime.datetime.now())
    app.run(debug=True, host=HOST, port=PORT)
