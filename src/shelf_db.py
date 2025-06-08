import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Shelf:
    """
    Класс, отвечающий за создание полки в базе данных
    """

    def __init__(self, index_of_shelf, rows):
        """
        Конструктор класса

        :param index_of_shelf: индекс полки (индекс брать из графа)
        :param rows: количество этажей в полке
        """
        self._index_of_shelf = index_of_shelf
        self._rows = rows
        self._number_of_filled = 0
        self._conn = psycopg2.connect(
            dbname="warehouse_db",
            user="robot",
            password="Access_for_robot_12345",
            host="localhost",
        )
        self._ensure_shelf_exists()

    def _ensure_shelf_exists(self):
        """
        Функция, проверяющая существование полки в базе
        """
        with self._conn.cursor() as cur:
            for row in range(1, self._rows + 1):
                cur.execute(
                    """
                    INSERT INTO shelves (shelf_index, row_index, is_filled)
                    VALUES (%s, %s, FALSE)
                    ON CONFLICT DO NOTHING
                """,
                    (self._index_of_shelf, row),
                )
            self._conn.commit()

    def __del__(self):
        self._conn.close()
