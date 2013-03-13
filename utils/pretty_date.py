import datetime, pytz

def local_date(time, tz='US/Eastern'):
    return pytz.timezone(tz).fromutc(time)

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.datetime.now()
    if type(time) in (int, float):
        diff = now - datetime.datetime.fromtimestamp(time)
    elif isinstance(time,datetime.datetime):
        if not time.tzname():
            time = pytz.utc.localize(time)
        now = datetime.datetime.now(pytz.utc)
        diff = now - time 
    else:
        diff = -1
        return "unknown"
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return pluralize_ago(day_diff/7, 'week')
    if day_diff < 365:
        return pluralize_ago(day_diff/30, 'month')
    return pluralize_ago(day_diff/365, 'year')

def pluralize_ago(n, span):
    return "%d %s%s ago" % (n, span, '' if n==1 else 's') 
