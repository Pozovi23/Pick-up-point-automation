from database_manager import DatabaseManager
from graph import Graph
from line_follower import LineFollower
from robot_platform import Platform
from shelf_db import Shelf
from shelf_scheduler import ShelfScheduler
import requests
import time
import math

class Warehouse:
    """
    Класс, координирующий весь склад
    """

    def __init__(self):
        """
        Конструктор класса

        Пересоздаем БД, создаем необходимое кол-во полок с необходимыми параметрами

        Считываем граф, отвечающий за планировку склада

        Ну и инициализируем по сути все составляющие робота
        """
        DatabaseManager.initialize(force_recreate=True)
        self._amount_of_shelves = 3
        self._shelves = [Shelf(i, 2) for i in range(1, self._amount_of_shelves + 1)]
        self._scheduler = ShelfScheduler()
        self._road_graph = Graph("graph.csv")
        self._current_follower = LineFollower()
        self._platform = Platform()
        self._robot_state = "requesting_box"  # requesting_box or grab_box or loading_onto_shelf or going_to_shelf or going_to_base
        self._curr_shelf = None
        self._curr_floor = None
        self._current_path = None
        self._box_id = 1
        self._conveyor_ip = "192.168.0.220"

    def movement_in_warehouse(
        self, departure, destination, ancestor_of_departure_place
    ):
        """
        Функция, осуществляющая движение робота из пункта A в пункт B

        :param departure: точка отправления
        :param destination: точка назначение
        :param ancestor_of_departure_place: предок(в терминологии графов) точки отправления. Необходим для правильной стартовой траектории движения
        """
        begin = departure
        end = destination
        self._current_path = [
            ancestor_of_departure_place
        ] + self._road_graph.find_shortest_path(begin, end)
        idx = 1

        while True:
            left = self._current_follower.left_turn_sensor.is_triggered()
            right = self._current_follower.right_turn_sensor.is_triggered()

            if left and right:
                self._current_follower.hard_stop()
                if idx + 1 == len(self._current_path):
                    break

                current_direction = self._road_graph.get_direction(
                    self._current_path[idx - 1],
                    self._current_path[idx],
                    self._current_path[idx + 1],
                )
                self._current_follower.handle_intersection(current_direction)
                idx += 1
            else:
                self._current_follower.move_straight()
        self._current_follower.hard_stop()

    def load_box(self, floor):
        """
        Функция, отвечающая за загрузку/выгрузку груза
        :param floor:
        """
        if floor == -1:
            self._platform.push_in_platform()
            self._platform.lower_until_endstop()
            self._platform.push_out_platform()
            self._platform.move(2, "up")
            self._platform.push_in_platform()
            self._platform.lower_until_endstop()

        elif floor == 0:
            self._platform.push_in_platform()
            self._platform.lower_until_endstop()
            self._platform.move(2, "up")
            self._platform.push_out_platform()
            self._platform.move(1, "down")
            self._platform.push_in_platform()
            self._platform.lower_until_endstop()

    def _get_box_id(self):
        """
        Функция, запрашивающая индекс следующей коробки у конвейера
        :return: индекс следующей коробки или -1 в случае ошибки
        """
        url = f"http://{self._conveyor_ip}/number"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return int(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error getting box ID: {e}")
            return -1
        except ValueError as e:
            print(f"Error parsing box ID: {e}")
            return -1

    def _notify_conveyor(self):
        """
        Функция, уведомляющая конвейер о том, что робот забрал коробку
        """
        url_1 = f"http://{self._conveyor_ip}/setNumber?number=1"
        url_0 = f"http://{self._conveyor_ip}/setNumber?number=0"
        try:
            response1 = requests.get(url_1, timeout=5)
            response1.raise_for_status()

            time.sleep(0.1)

            response0 = requests.get(url_0, timeout=5)
            response0.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"Error notifying conveyor: {e}")

    def work(self):
        """
        Общий цикл программы
        """
        while True:
            if self._robot_state == "requesting_box":
                self._box_id = self._get_box_id()
                if 0 <= self._box_id <= math.inf:
                    self._robot_state = "grab_box"
                    print(f"got id = {self._box_id}")
                else:
                    print("No boxes")
                    time.sleep(5)


            elif self._robot_state == "grab_box":
                self.load_box(-1)
                print(f"grabbed box")
                self._notify_conveyor()
                self._robot_state = "going_to_shelf"

            elif self._robot_state == "going_to_shelf":
                print(self._box_id)
                self._curr_shelf, self._curr_floor = (
                    self._scheduler.fill_nearest_empty_cell(self._box_id)
                )
                self._curr_floor -= 1
                print(self._curr_shelf, self._curr_floor)
                self.movement_in_warehouse(
                    "base", f"Shelf_{self._curr_shelf}", "Crossroad_4"
                )
                self._robot_state = "loading_onto_shelf"

            elif self._robot_state == "loading_onto_shelf":
                self.load_box(self._curr_floor)
                self._robot_state = "going_to_base"

            elif self._robot_state == "going_to_base":
                curr_ancestor = self._current_path[-2]
                self.movement_in_warehouse(
                    f"Shelf_{self._curr_shelf}", "base", curr_ancestor
                )
                self._robot_state = "requesting_box"
