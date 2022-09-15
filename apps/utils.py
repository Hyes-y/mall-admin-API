from django.conf import settings
from apps.coupon.models import Coupon

import os
import json
from random import seed, random
from datetime import datetime, timedelta
from decimal import Decimal

import requests

# 배송비 데이터 로드
with open(os.path.join(settings.BASE_DIR, 'apps', 'data', 'delivery_cost.json'), "r") as f:
    delivery_cost_data = json.load(f)

# 국가명 - 코드 데이터 로드
with open(os.path.join(settings.BASE_DIR, 'apps', 'data', 'country_code.json'), "r") as f:
    country_code_data = json.load(f)


def code_generator(s):
    """
    쿠폰 코드 생성 함수
    12자리 숫자 코드를 반환하며 중복을 허용하지 않음
    input: s
    return: str(12)
    """
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
    """ 현재 날짜 반환 함수 (str, YYYY-mm-dd HH:MM:SS) """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def add_period(issue_date, period):
    """
    날짜 더하기 함수
    input: issue_date, period(day)
    return: str(YYYY-mm-dd HH:MM:SS)
    """
    expired_date = datetime.strptime(issue_date, '%Y-%m-%d %H:%M:%S') + timedelta(days=period)
    return expired_date.strftime('%Y-%m-%d %H:%M:%S')


def exchange_currency(amount, currency='krw'):
    """
    원 - 달러 변환 함수
    현재 일자 환율 정보를 이용하여 원 - 달러 변환
    amount: 금액
    currency: 변환하고자 하는 통화 코드('krw', 'usd')

    input: amount(decimal), currency(str, default='krw')
    return: Decimal
    """
    file_path = os.path.join(settings.BASE_DIR,
                             'apps',
                             'data',
                             'exchange_rate',
                             f'{get_current_date()}.json')

    # 오늘 환율이 이미 저장된 경우
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            file = json.load(f)
            return amount / Decimal(file['USD']) if currency == 'usd' else amount * Decimal(file['USD'])
    # 오늘 환율이 저장되어 있지 않은 경우
    else:
        url = 'https://www.koreaexim.go.kr/site/program/financial'
        api = '/exchangeJSON'
        params = {
            'authkey': settings.ER_API_KEY,
            'data': 'AP01',
        }
        response = requests.get(f'{url}{api}', params=params).json()

        for res in response:
            # cur_unit : 통화코드
            # deal_bas_r : 매매기준율(환율)
            if res['cur_unit'] == "USD":
                # 천 단위 구분 기호(,) 제거
                exchange_rate = res['deal_bas_r'].replace(",", "")
                data = {
                    'USD': exchange_rate
                }
                with open(file_path, 'w') as wf:
                    json.dump(data, wf)
                return amount / Decimal(data['USD']) if currency == 'usd' else amount * Decimal(data['USD'])


def get_exchange_rate(date=None):
    """
    원 - 달러 환율 반환 함수
    date: 환율 조회하고 싶은 날짜(default=None)

    input: date
    return: Decimal
    """
    file_path = os.path.join(settings.BASE_DIR,
                             'apps',
                             'data',
                             'exchange_rate',
                             f'{get_current_date()[:10]}.json')

    # 오늘 환율이 이미 저장된 경우
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            file = json.load(f)
            return Decimal(file['USD'])
    # 오늘 환율이 저장되어 있지 않은 경우
    else:
        url = 'https://www.koreaexim.go.kr/site/program/financial'
        api = '/exchangeJSON'
        params = {
            'authkey': settings.ER_API_KEY,
            'data': 'AP01',
        }
        response = requests.get(f'{url}{api}', params=params).json()

        for res in response:
            # cur_unit : 통화코드
            # deal_bas_r : 매매기준율(환율)
            if res['cur_unit'] == "USD":
                # 천 단위 구분 기호(,) 제거
                exchange_rate = res['deal_bas_r'].replace(",", "")
                data = {
                    'USD': exchange_rate
                }
                with open(file_path, 'w') as wf:
                    json.dump(data, wf)
                return Decimal(data['USD'])


def get_delivery_cost(country, quantity):
    """
    국가별 개수별 배송비 반환 함수 (원화(KRW))
    데이터에 없는 국가의 경우 미국 배송비를 기준
    input: country(str, ex. 'KR'), quantity(int)
    output: int
    """
    try:
        country_name = country_code_data[country]['country_name']
        delivery_cost = delivery_cost_data[country_name][str(quantity)]
    except KeyError:
        country_name = "USA"

    finally:
        delivery_cost = delivery_cost_data[country_name][str(quantity)]

    return delivery_cost
