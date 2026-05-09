#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import pytest

from callattendant.userinterface.webapp import app, get_random_string, get_db


# Load SQL test dataset
SQL_PATH = os.path.join(os.path.dirname(__file__), "callattendant.db.sql")
with open(SQL_PATH, "r", encoding="utf-8") as f:
    _data_sql = f.read()


@pytest.fixture(scope="function")
def myapp():
    """
    Create a fully isolated Flask app for each test.
    """

    db_fd, db_path = tempfile.mkstemp()

    # IMPORTANT: prevent config leakage between tests
    app.config.clear()

    app.secret_key = get_random_string()

    app.config.update({
        "TESTING": True,
        "DEBUG": True,
        "MASTER_CONFIG": {
            "DB_FILE": db_path,
            "PHONE_DISPLAY_FORMAT": "###-###-####",
            "PHONE_DISPLAY_SEPARATOR": "-",
        },
    })

    with app.app_context():
        db = get_db()
        db.executescript(_data_sql)
        db.commit()

    yield app

    # cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def client(myapp):
    """
    Test client bound to isolated app instance.
    """
    return myapp.test_client()


def test_dashboard(client):
    response = client.get("/", follow_redirects=True)

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Statistics" in response.data
    assert b"Recent Calls" in response.data
    assert b"Calls per Day" in response.data
