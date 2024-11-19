import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("MARKET_DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TRADING_HISTORY_URL = os.getenv("TRADING_HISTORY_URL", "http://trading_history:5000/trading_history/")
    COLLECTION_URL = os.getenv("COLLECTION_URL", "http://collection:5000/collection/")
    DBM_URL = os.getenv("DBM_URL", "http://db_manager:5000/db_manager/")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
