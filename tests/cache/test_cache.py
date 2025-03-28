from unittest.mock import Mock

import pytest
import xinfo.cache as cache

OBJ = {"a": 10, "b": 20}


@pytest.fixture
def mock_func():
    """Sample function passed to the cache routine."""
    mock = Mock()
    mock.return_value = OBJ
    yield mock


@pytest.fixture
def tmp_cache_dir(tmp_path):
    """Overwrite the default cache directory with a temporary one."""
    cache.CACHE_DIR = tmp_path
    yield


def test_force_should_always_call_func(tmp_cache_dir, mock_func):
    """lazy_load with force should always call the passed function."""
    for i in range(2):
        obj = cache.lazy_load("test.data", force=True, func=mock_func)
        assert obj == OBJ
        assert mock_func.call_count == i + 1


def test_func_is_called_when_no_data_in_cache(tmp_cache_dir, mock_func):
    """The callback function should be called when no data in cache."""
    obj = cache.lazy_load("test.data", force=False, func=mock_func)
    assert obj == OBJ
    mock_func.assert_called_once_with()


def test_func_is_not_called_when_data_in_cache(tmp_cache_dir, mock_func):
    """The callback function should not be called when data is in cache."""
    obj = cache.lazy_load("test.data", False, mock_func, "arg1", "arg2")
    assert obj == OBJ
    mock_func.assert_called_once_with("arg1", "arg2")
    mock_func.reset_mock()
    obj = cache.lazy_load("test.data", False, mock_func, "arg1", "arg2")
    assert obj == OBJ
    mock_func.assert_not_called()
