from random import seed
from random import random

from datetime import datetime, timedelta
from apps.coupon.models import Coupon
from django.conf import settings
import json
import os

with open(os.path.join(settings.BASE_DIR, 'apps', 'data', 'delivery_cost.json'), "r") as f:
    delivery_cost_data = json.load(f)

with open(os.path.join(settings.BASE_DIR, 'apps', 'data', 'country_code.json'), "r") as f:
    country_code_data = json.load(f)


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


def get_dollar(krw):
    return krw // 1200


def get_delivery_cost(country, quantity):
    country_name = country_code_data[country]['country_name']
    delivery_cost = delivery_cost_data[country_name][str(quantity)]
    return delivery_cost
