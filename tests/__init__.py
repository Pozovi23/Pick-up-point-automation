import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest


@pytest.fixture
def db_connection():
    import psycopg2

    conn = psycopg2.connect(
        dbname="warehouse_db",
        user="robot",
        password="Access_for_robot_12345",
        host="localhost",
    )
    yield conn
    conn.close()
