import os
import secrets

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(16)
    DEBUG = True
    
