from flask import Flask
from routes import api_blueprint, consensus_blueprint
from routes import pn


def app_factory():
    app = Flask(__name__)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(consensus_blueprint)

    # Add our component objects here. Pass references of app so they can use them too
    with app.app_context():
        pn.init_app(app)
    return app
