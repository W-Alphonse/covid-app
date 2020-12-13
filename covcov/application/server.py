import datetime
from flask import Flask, jsonify, request
from covcov.infrastructure.configuration.config import config

from covcov.application import route_dispatcher

# Flask object and properties
from covcov.infrastructure.db.database import Database

app = Flask(__name__)
PORT = config["api"]["port"]
HOST = config["api"]["host"]

db = Database("database")

@app.route("/company_domain", methods=["POST"])
def subscription_api():
    return jsonify(route_dispatcher.dispatch(request.get_json(), db))


@app.route("/example", methods=["GET"])
def example():
    try:
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
