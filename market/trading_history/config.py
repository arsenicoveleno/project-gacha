import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("MARKET_DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DBM_URL = os.getenv("DBM_URL", "http://db_manager:5000/db_manager/")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
