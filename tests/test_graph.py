import os

import pytest

from src.graph import Graph


@pytest.fixture
def graph():
    # Create a temporary CSV file for testing
    test_csv = "test_graph.csv"
    with open(test_csv, "w") as f:
        f.write(
            """previous,from,to,direction
Crossroad_4,base,Crossroad_1,forward
base,Crossroad_1,Crossroad_2,right
Crossroad_1,Crossroad_2,Shelf_1,right"""
        )

    yield Graph(test_csv)
    os.remove(test_csv)


def test_graph_initialization(graph):
    assert graph._graph == {
        "base": {"Crossroad_1": {"Crossroad_4": "forward"}},
        "Crossroad_1": {"Crossroad_2": {"base": "right"}},
        "Crossroad_2": {"Shelf_1": {"Crossroad_1": "right"}},
    }


def test_get_direction(graph):
    assert graph.get_direction("Crossroad_4", "base", "Crossroad_1") == "forward"
    assert graph.get_direction("base", "Crossroad_1", "Crossroad_2") == "right"
    assert graph.get_direction("Crossroad_1", "Crossroad_2", "Shelf_1") == "right"


def test_find_shortest_path(graph):
    assert graph.find_shortest_path("base", "Shelf_1") == [
        "base",
        "Crossroad_1",
        "Crossroad_2",
        "Shelf_1",
    ]
    assert graph.find_shortest_path("Crossroad_1", "Shelf_1") == [
        "Crossroad_1",
        "Crossroad_2",
        "Shelf_1",
    ]
    assert (
        graph.find_shortest_path("Shelf_1", "base") is None
    )  # No reverse path in this test graph
