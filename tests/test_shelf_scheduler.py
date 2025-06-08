import pytest
from src.shelf_scheduler import ShelfScheduler
from src.shelf_db import Shelf
from src.database_manager import DatabaseManager


@pytest.fixture
def scheduler():
    DatabaseManager.initialize(force_recreate=True)
    # Create some shelves with empty cells
    Shelf(1, 3)
    Shelf(2, 3)
    yield ShelfScheduler()


def test_find_nearest_empty_cell(scheduler):
    # Should find the first empty cell in shelf 1, row 1
    cell = scheduler.find_nearest_empty_cell()
    assert cell == (1, 1)


def test_fill_nearest_empty_cell(scheduler):
    # Fill first cell
    result = scheduler.fill_nearest_empty_cell(1001)
    assert result == (1, 1)

    # Next empty cell should be (1, 2)
    cell = scheduler.find_nearest_empty_cell()
    assert cell == (1, 2)


def test_find_item_location(scheduler):
    # Fill a cell and then find it
    scheduler.fill_nearest_empty_cell(1002)
    location = scheduler.find_item_location(1002)
    assert location == (1, 1)

    # Non-existent item
    assert scheduler.find_item_location(9999) is None