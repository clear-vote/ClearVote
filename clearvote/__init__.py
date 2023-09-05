from flask import Flask
import secrets
from flask_wtf import CSRFProtect
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

if __name__ == "__main__":
    app.run()

from clearvote import views