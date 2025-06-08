import csv
import os
from collections import deque


class Graph:
    """
    Класс, отвечающий за граф склада и взаимодействие с ним(кратчайший путь, направление движения)
    """

    def __init__(self, path_to_csv=None):
        """
        Конструктор класса

        Открываем csv файл, парсим его и создаём граф склада

        :param path_to_csv: путь к csv файл где описывается граф
        """
        path_to_csv = path_to_csv if path_to_csv else os.path.join(os.path.dirname(__file__), 'graph.csv')
        self._graph = {}
        with open(path_to_csv, "r") as file:
            reader = csv.reader(file)
            next(reader)  # skip header
            for line in reader:
                if self._graph.get(line[1]) is None:
                    self._graph[line[1]] = {}

                if self._graph.get(line[1]).get(line[2]) is None:
                    self._graph[line[1]][line[2]] = {}

                self._graph[line[1]][line[2]][line[0]] = line[3]

    def get_direction(self, ancestor, begin, end):
        """
        Функция, определяющая направление следующего движения робота

        :param ancestor: узел, предшествующий тому, из которого происходит отправление.
            Нужен для правильного направления движения

        :param begin: узел, из которого происходит отправление

        :param end: узел, в который прибывает робот

        :return: направление движения робота(right, left, forward)
        """
        return self._graph[begin][end][ancestor]

    def find_shortest_path(self, start, end):
        """
        Функция, вычисляющая кратчайший путь из start в end.
            Это BFS, так как в нашем случае грани графа не являются взвешенными.
            Если делать это для настоящего склада, то для лучшей оптимизации нужно замерять длины граней и использовать алгоритм Дейкстры

        :param start: пункт отбытия

        :param end: пункт прибытия

        :return: кратчайший путь из start в end
        """

        if start not in self._graph:
            return None

        end_in_graph = False
        for key in self._graph.keys():
            if list(self._graph[key].keys())[0] == end:
                end_in_graph = True

        if not end_in_graph:
            return None

        queue = deque()
        queue.append([start])
        visited = set()
        visited.add(start)
        while queue:
            path = queue.popleft()
            node = path[-1]

            if node == end:
                return path

            for neighbor in self._graph.get(node, {}).keys():
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return None
