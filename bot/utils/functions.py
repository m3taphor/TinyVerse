import random
import datetime

def unix_convert(unix: int):
    date_time = datetime.datetime.fromtimestamp(unix)

    return date_time.strftime('%b %d, %Y')