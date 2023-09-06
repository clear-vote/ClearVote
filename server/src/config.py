import os
import secrets

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(16)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    DEBUG = True