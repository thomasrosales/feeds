def get_next_retry_countdown(retry_step: str):
    return {
        "1": 2 * 60,  # 2 minutes
        "2": 5 * 60,  # 5 minutes
        "3": 8 * 60,  # 8 minutes
    }.get(retry_step, 180)
