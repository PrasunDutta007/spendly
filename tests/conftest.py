import os
import tempfile

import pytest

import database.db as db_module
import app as app_module


@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    original_path = db_module.DB_PATH
    db_module.DB_PATH = path
    db_module.init_db()
    db_module.seed_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client
    db_module.DB_PATH = original_path
    os.remove(path)
