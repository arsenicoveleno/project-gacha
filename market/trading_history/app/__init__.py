from flask import Flask
from .routes import trading_history
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .models import db
    db.init_app(app)
    app.register_blueprint(trading_history, url_prefix='/trading_history')

    return app

