import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
DB_NAME_TEST = os.getenv("DB_NAME_TEST")

_client = None


def _get_client():
    global _client
    if _client is None:
        if not MONGODB_URI:
            raise RuntimeError("MONGO_URI environment variable is not set")
        _client = MongoClient(MONGODB_URI)
    return _client


def get_db():
    if not DB_NAME:
        raise RuntimeError("DB_NAME environment variable is not set")
    return _get_client()[DB_NAME]


def get_db_test():
    if not DB_NAME_TEST:
        raise RuntimeError("DB_NAME_TEST environment variable is not set")
    return _get_client()[DB_NAME_TEST]


# Lazy proxies for backward compatibility
class _LazyDB:
    """Proxy that defers MongoDB connection until first attribute access."""
    def __init__(self, getter):
        self._getter = getter

    def __getattr__(self, name):
        return getattr(self._getter(), name)

    def __getitem__(self, name):
        return self._getter()[name]


db = _LazyDB(get_db)
db_test = _LazyDB(get_db_test)