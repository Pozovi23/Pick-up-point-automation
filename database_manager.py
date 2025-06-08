import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DatabaseManager:
    """
    Класс(ну или по факту метод), отвечающий  за удалению старой базы данных и создание новой, чистой
    """
    @staticmethod
    def initialize(force_recreate=False):
        conn = psycopg2.connect(
            dbname="postgres",
            user="robot",
            password="Access_for_robot_12345",
            host="localhost",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            with conn.cursor() as cur:
                if force_recreate:
                    cur.execute("DROP DATABASE IF EXISTS warehouse_db")
                cur.execute("CREATE DATABASE warehouse_db")

            conn = psycopg2.connect(
                dbname="warehouse_db",
                user="robot",
                password="Access_for_robot_12345",
                host="localhost",
            )

            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS shelves (
                        shelf_index INTEGER NOT NULL,
                        row_index INTEGER NOT NULL,
                        is_filled BOOLEAN DEFAULT FALSE,
                        item_number INTEGER,
                        PRIMARY KEY (shelf_index, row_index)
                    )
                """
                )
                conn.commit()
        finally:
            conn.close()
