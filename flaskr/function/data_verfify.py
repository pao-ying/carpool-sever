from datetime import datetime


def is_none(array):
    for data in array:
        if data is None:
            return True
    return False


def is_int(data):
    try:
        data = int(data)
    except ValueError:
        return 'error'
    return data


def is_date(data):
    try:
        data = datetime.strptime(data, '%Y-%m-%d %H:%M')
    except ValueError:
        return 'error'
    return data


def is_small(first, second):
    if datetime.strptime(first, '%Y-%m-%d %H:%M') <= datetime.strptime(second, '%Y-%m-%d %H:%M'):
        return False
    else:
        return True