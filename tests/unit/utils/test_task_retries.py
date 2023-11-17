import pytest

from feeds_for_sendcloud.utils.task_retries import generate_next_retry_countdown


@pytest.mark.parametrize(
    "retry_index,expected",
    (
        (0, 120),
        (1, 300),
        (2, 480),
        (3, 660),
        (100, 18120),
    ),
)
def test_generate_next_retry_countdown(retry_index, expected):
    assert generate_next_retry_countdown(retry_index) == expected
