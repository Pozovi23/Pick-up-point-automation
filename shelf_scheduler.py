import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class ShelfScheduler:
    """
    Класс, отвечающий за все полки на складе
    """
    def __init__(self):
        """
        Конструктор класса
        """
        self._conn = psycopg2.connect(
            dbname="warehouse_db",
            user="robot",
            password="Access_for_robot_12345",
            host="localhost",
        )

    def find_nearest_empty_cell(self):
        """
        Функция, которая находит ближайшую пустую ячейку среди всех полок
        """
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT shelf_index, row_index 
                FROM shelves 
                WHERE is_filled = FALSE 
                ORDER BY shelf_index ASC, row_index ASC 
                LIMIT 1
            """
            )
            return cur.fetchone()

    def fill_nearest_empty_cell(self, item_number):
        """
        Функция, которая заполняет ближайшую пустую ячейку указанным номером

        :param item_number: уникальный номер предмета
        :return: индекс полки и этажа
        """
        cell = self.find_nearest_empty_cell()
        if cell:
            shelf_idx, row_idx = cell
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE shelves 
                    SET is_filled = TRUE, item_number = %s
                    WHERE shelf_index = %s AND row_index = %s
                    RETURNING shelf_index, row_index
                """,
                    (item_number, shelf_idx, row_idx),
                )
                result = cur.fetchone()
                self._conn.commit()
                return result
        return None

    def find_item_location(self, item_number):
        """
        Функция, которая находит местоположение предмета по его номеру(в разработке)

        :param item_number: номер предмета
        :return:
        """
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT shelf_index, row_index 
                FROM shelves 
                WHERE item_number = %s
            """,
                (item_number,),
            )
            return cur.fetchone()

    def __del__(self):
        self._conn.close()
