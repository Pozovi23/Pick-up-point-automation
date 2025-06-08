import pytest
from src.database_manager import DatabaseManager
import psycopg2


def test_database_initialization():
    # Test database creation and table setup
    DatabaseManager.initialize(force_recreate=True)

    conn = psycopg2.connect(
        dbname="warehouse_db",
        user="robot",
        password="Access_for_robot_12345",
        host="localhost",
    )

    try:
        with conn.cursor() as cur:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'shelves'
                )
            """)
            assert cur.fetchone()[0] is True

            # Check table structure
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'shelves'
            """)
            columns = {row[0]: row[1] for row in cur.fetchall()}
            expected_columns = {
                'shelf_index': 'integer',
                'row_index': 'integer',
                'is_filled': 'boolean',
                'item_number': 'integer'
            }
            assert columns == expected_columns
    finally:
        conn.close()