import datetime
from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS

from covcov.infrastructure.configuration.config import config

from covcov.application import route_dispatcher

# Flask object and properties
from covcov.infrastructure.db.database import Database

app = Flask(__name__)
PORT = config["api"]["port"]
HOST = config["api"]["host"]
#
#CORS(app)
CORS(app, supports_credentials=True)
#app.config['CORS_HEADERS'] = 'Content-Type'

db = Database("database")

@app.route("/company_domain", methods=["POST"])
@cross_origin(headers=['Content-Type'])
def subscription_api():
    return jsonify(route_dispatcher.dispatch(request.get_json(), request.args, db))

@app.route("/visit_domain", methods=["POST"])
def visit_api():
    return jsonify(route_dispatcher.dispatch(request.get_json(), request.args, db))


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

# @app.before_first_request
# def before_start():
#     db.create_tables()

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()

if __name__ == "__main__":
    print("starting API at", datetime.datetime.now())
    app.run(debug=True, host=HOST, port=PORT)