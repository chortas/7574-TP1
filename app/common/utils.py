from datetime import datetime

FULL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MINUTE_FORMAT = "%Y-%m-%d %H:%M"
DATE_FORMAT = "%Y-%m-%d"

def get_and_format_datetime_now():
    return datetime.now().strftime(FULL_DATE_FORMAT)
