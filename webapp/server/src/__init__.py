from flask import Flask
from .config import Config
from flask_wtf.csrf import CSRFProtect

def create_app(config_class=Config):
    app = Flask(__name__)    

    app.config.from_object(Config)

    csrf = CSRFProtect()
    csrf.init_app(app)

    from src import views
    views.init_app(app)
    
    return app