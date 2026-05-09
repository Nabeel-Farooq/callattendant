#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pytest
from typing import Dict, Generator

from callattendant.screening.calllogger import CallLogger


@pytest.fixture
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Create a fresh in-memory SQLite DB per test.
    """

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # NOTE:
    # Only define schema here if CallLogger does NOT manage it internally.
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS call_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            number TEXT,
            date TEXT,
            time TEXT,
            status TEXT,
            reason TEXT
        );
    """)
    conn.commit()

    yield conn

    conn.close()


@pytest.fixture
def config() -> Dict[str, bool]:
    """
    Mock configuration used by CallLogger.
    """
    return {
        "DEBUG": True,
        "TESTING": True,
    }


@pytest.fixture
def calllogger(db_connection, config) -> CallLogger:
    """
    Fresh CallLogger instance per test.
    """
    return CallLogger(db_connection, config)


def test_add_caller_increments_sequentially(calllogger: CallLogger):
    """
    Ensure that calls are logged sequentially.
    """

    caller = {
        "NAME": "Bruce",
        "NMBR": "1234567890",
        "DATE": "1012",
        "TIME": "0600",
    }

    first_id = calllogger.log_caller(caller, "Permitted", "Test1")
    second_id = calllogger.log_caller(caller)

    assert second_id == first_id + 1
