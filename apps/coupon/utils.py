from random import seed
from random import random
from datetime import datetime, timedelta
from .models import Coupon


def code_generator(s):
    seed(s)
    while True:
        value = str(random())[2:]
        if len(value) >= 12:
            value = value[:12]
            if len(Coupon.objects.filter(code=value)) == 0:
                return value
        else:
            continue


def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')


def add_period(issue_date, period):
    expired_date = datetime.strptime(issue_date, '%Y-%m-%d') + timedelta(days=period)
    return expired_date.strftime('%Y-%m-%d')
