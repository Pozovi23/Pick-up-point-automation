import psycopg2
import pytest

from src.database_manager import DatabaseManager
from src.shelf_db import Shelf


@pytest.fixture(scope="module")
def setup_db():
    DatabaseManager.initialize(force_recreate=True)
    yield
    # Cleanup after all tests


def test_shelf_initialization(setup_db):
    shelf = Shelf(1, 5)

    conn = psycopg2.connect(
        dbname="warehouse_db",
        user="robot",
        password="Access_for_robot_12345",
        host="localhost",
    )

    try:
        with conn.cursor() as cur:
            # Check if rows were created
            cur.execute(
                """
                SELECT COUNT(*) 
                FROM shelves 
                WHERE shelf_index = 1
            """
            )
            assert cur.fetchone()[0] == 5

            # Check initial state
            cur.execute(
                """
                SELECT COUNT(*) 
                FROM shelves 
                WHERE shelf_index = 1 AND is_filled = FALSE
            """
            )
            assert cur.fetchone()[0] == 5
    finally:
        conn.close()
