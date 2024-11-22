import random
import datetime

def gen_xapi(lid=None, mid=None, appid=None):
    return f"{lid}:{mid}:{appid}:{str(random.random())}"

def unix_convert(unix: int):
    date_time = datetime.datetime.fromtimestamp(unix)

    return date_time.strftime('%b %d, %Y')