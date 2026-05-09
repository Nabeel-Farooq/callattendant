#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pytest
from typing import Dict, Generator, Any

from callattendant.screening.calllogger import CallLogger


@pytest.fixture(scope="function")
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Creates a fresh in-memory SQLite database per test.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # If CallLogger expects tables, initialize them here
    # (adjust schema based on your actual implementation)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS call_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            number TEXT,
            date TEXT,
            time TEXT,
            status TEXT,
            reason TEXT
        )
    """)
    conn.commit()

    yield conn

    conn.close()


@pytest.fixture(scope="function")
def config() -> Dict[str, Any]:
    """
    Mock application configuration.
    """
    return {
        "DEBUG": True,
        "TESTING": True,
    }


@pytest.fixture(scope="function")
def calllogger(db_connection, config) -> CallLogger:
    """
    Creates a fresh CallLogger instance for each test.
    """
    return CallLogger(db_connection, config)


def test_add_caller(calllogger: CallLogger):
    """
    Verify that call logging increments correctly.
    """

    callerid = {
        "NAME": "Bruce",
        "NMBR": "1234567890",
        "DATE": "1012",
        "TIME": "0600",
    }

    first_result = calllogger.log_caller(callerid, "Permitted", "Test1")
    assert first_result == 1, "First log entry should return ID 1"

    second_result = calllogger.log_caller(callerid)
    assert second_result == 2, "Second log entry should return ID 2"
