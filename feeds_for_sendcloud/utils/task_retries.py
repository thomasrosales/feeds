import deprecation
import feeds_for_sendcloud


@deprecation.deprecated(
    deprecated_in="0.1.0",
    removed_in="0.2.0",
    current_version=feeds_for_sendcloud.__version__,
    details="Use the generate_next_retry_countdown function instead"
)
def get_next_retry_countdown(retry_step: str) -> int:
    return {
        "1": 2 * 60,  # 2 minutes
        "2": 5 * 60,  # 5 minutes
        "3": 8 * 60,  # 8 minutes
    }.get(retry_step, 180)


def generate_next_retry_countdown(retry_step: int) -> int:
    """
    It represents a lineal function given the following points:
    (0, 2)
    (1, 5)
    (2, 8)

    p=3 (constant term)
    q=2 (coefficient of the independent variable)

    f(x) = px + q
    f(x) = 3x + 2

    This function returns the next countdown time in seconds given the retry step.
    """
    return (3 * retry_step + 2) * 60
