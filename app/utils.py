# app/utils.py

from datetime import datetime

def parse_datetime_string(dt_str):
    return datetime.fromisoformat(dt_str)
