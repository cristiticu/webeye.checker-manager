from datetime import datetime, timedelta


def is_after_24_hours(earlier: datetime, later: datetime):
    return later - earlier > timedelta(hours=24)
