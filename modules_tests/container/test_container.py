import pytest
import warnings
from container.container_handler import get_optimal_series_container, get_series_container_min_height
from data.models import Series, SeriesContainer

warnings.filterwarnings("ignore", category=DeprecationWarning)

@pytest.fixture
def series():
    series_data = {
        "name": "Test Series",
        "year": 2025,
        "stamps": [
            {"height": 2.0, "width": 1.0},
            {"height": 2.0, "width": 1.5},
            {"height": 2.0, "width": 2.0},
            {"height": 2.0, "width": 2.5},
            {"height": 2.0, "width": 3.0}
        ]
    }
    return Series(series_data)

def test_get_series_container_min_height(series):
    max_width = 6.5
    stamp_padding = 0.5
    container = get_series_container_min_height(series, max_width, stamp_padding)
    assert isinstance(container, SeriesContainer)
    assert container.height > 0
    assert container.width > 0
    assert len(container.rows) > 0

def test_get_optimal_series_container(series):
    max_width = 6.5
    stamp_padding = 0.5
    container = get_optimal_series_container(series, max_width, stamp_padding)
    assert isinstance(container, SeriesContainer)
    assert container.height > 0
    assert container.width > 0
    assert len(container.rows) > 0

def test_empty_series():
    series_data = {
        "name": "Empty Series",
        "year": 2025,
        "stamps": []
    }
    series = Series(series_data)
    max_width = 6.5
    stamp_padding = 0.5
    container = get_series_container_min_height(series, max_width, stamp_padding)
    assert isinstance(container, SeriesContainer)
    assert container.height == 0
    assert container.width == 0
    assert len(container.rows) == 0

def test_single_stamp_series():
    series_data = {
        "name": "Single Stamp Series",
        "year": 2025,
        "stamps": [
            {"height": 2.0, "width": 1.0}
        ]
    }
    series = Series(series_data)
    max_width = 6.5
    stamp_padding = 0.5
    container = get_series_container_min_height(series, max_width, stamp_padding)
    assert isinstance(container, SeriesContainer)
    assert container.height > 0
    assert container.width > 0
    assert len(container.rows) == 1
    assert len(container.rows[0].stamp_containers) == 1