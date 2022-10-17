from datetime import datetime, timedelta
from copy import copy


def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def formatted_and_day_later(date: datetime) -> tuple:
    day_later = date + timedelta(days=1)
    return (format_date(date), format_date(day_later))
