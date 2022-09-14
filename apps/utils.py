from random import seed
from random import random

from datetime import datetime, timedelta
from apps.coupon.models import Coupon
from django.conf import settings
from decimal import Decimal
import requests
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
    file_path = os.path.join(settings.BASE_DIR,
                             'apps',
                             'data',
                             'exchange_rate',
                             f'{get_current_date()}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            file = json.load(f)
            return krw / Decimal(file['USD'])
    else:
        url = 'https://www.koreaexim.go.kr/site/program/financial'
        api = '/exchangeJSON'
        params = {
            'authkey': settings.ER_API_KEY,
            'data': 'AP01',
        }
        response = requests.get(f'{url}{api}', params=params).json()
        print(response)
        for res in response:
            if res['cur_unit'] == "USD":
                exchange_rate = res['deal_bas_r'].replace(",", "")
                data = {
                    'USD': exchange_rate
                }
                with open(file_path, 'w') as wf:
                    json.dump(data, wf)
                return krw / Decimal(data['USD'])


def get_delivery_cost(country, quantity):
    country_name = country_code_data[country]['country_name']
    delivery_cost = delivery_cost_data[country_name][str(quantity)]
    return delivery_cost
