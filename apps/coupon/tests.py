from rest_framework import status
from rest_framework.test import APITestCase

from apps.coupon.models import Coupon, CouponType
from apps.utils import get_current_date, add_period, code_generator


class CouponTest(APITestCase):
    """
    쿠폰 타입, 쿠폰 발급 테스트
    """
    def setUp(self):
        """ test 를 위한 mock 데이터 추가 """
        self.coupon_type_test_url = "/api/v1/admin/coupons/types/"
        self.coupon_test_url = "/api/v1/admin/coupons/"
        self.user = 1

        self.coupon_type = CouponType.objects.create(
            start_date="2022-09-13 00:00:00",
            end_date="2022-10-16 00:00:00",
            period=7,
            min_price=50000,
            max_dc_price=15000,
            dc_type=0,
            iss_type=0,
            description="배송비 할인 쿠폰"
        )

        self.coupon_type_for_duplicate = CouponType.objects.create(
            start_date="2022-09-13 00:00:00",
            end_date="2022-10-16 00:00:00",
            period=7,
            min_price=50000,
            max_dc_price=15000,
            dc_type=0,
            iss_type=0,
            description="배송비 할인 쿠폰"
        )

        self.coupon_type_expired = CouponType.objects.create(
            start_date="2022-09-13 00:00:00",
            end_date="2022-09-15 00:00:00",
            period=7,
            min_price=50000,
            max_dc_price=15000,
            dc_type=0,
            iss_type=0,
            description="배송비 할인 쿠폰"
        )

        self.coupon_type_inactive = CouponType.objects.create(
            start_date="2022-09-13 00:00:00",
            end_date="2022-10-16 00:00:00",
            period=7,
            min_price=50000,
            max_dc_price=15000,
            dc_type=0,
            iss_type=0,
            description="배송비 할인 쿠폰",
            is_active=False
        )

        self.coupon = Coupon.objects.create(
            type=self.coupon_type_for_duplicate,
            expired_date=add_period(get_current_date(), self.coupon_type.period),
            is_used=False,
            owner=self.user,
            code=code_generator(1)
        )

    def test_create_coupon_type_success(self):
        """ 쿠폰 타입 생성 성공 테스트 """

        data = {
            "start_date": "2022-09-13 00:00:00",
            "end_date": "2022-09-17 00:00:00",
            "period": 7,
            "min_price": 50000,
            "max_dc_price": 15000,
            "dc_type": 2,
            "iss_type": 0,
            "value": 10000,
            "description": "10000원 할인 쿠폰"
        }

        request_url = self.coupon_type_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_coupon_type_fail_due_to_value(self):
        """ 쿠폰 타입 생성 실패 테스트 : 100% 초과 할인 쿠폰 """

        data = {
            "start_date": "2022-09-13 00:00:00",
            "end_date": "2022-09-17 00:00:00",
            "period": 7,
            "min_price": 50000,
            "max_dc_price": 15000,
            "dc_type": 1,
            "iss_type": 0,
            "value": 150,
            "description": "150% 할인 쿠폰"
        }

        request_url = self.coupon_type_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_coupon_type_fail_due_to_date(self):
        """ 쿠폰 타입 생성 실패 테스트 : 유효 기간 종료 날짜가 현재 보다 이전인 경우 """

        data = {
            "start_date": "2022-09-13 00:00:00",
            "end_date": "2022-09-15 00:00:00",
            "period": 7,
            "min_price": 50000,
            "max_dc_price": 15000,
            "dc_type": 1,
            "iss_type": 0,
            "value": 15,
            "description": "15% 할인 쿠폰"
        }

        request_url = self.coupon_type_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_coupon_type_fail_due_to_date2(self):
        """ 쿠폰 타입 생성 실패 테스트 : 유효 기간 종료 날짜가 시작 날짜 보다 이전인 경우 """

        data = {
            "start_date": "2022-09-18 00:00:00",
            "end_date": "2022-09-17 00:00:00",
            "period": 7,
            "min_price": 50000,
            "max_dc_price": 15000,
            "dc_type": 1,
            "iss_type": 0,
            "value": 15,
            "description": "15% 할인 쿠폰"
        }

        request_url = self.coupon_type_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_coupon_success(self):
        """ 쿠폰 발급 성공 테스트  """

        data = {
            "type": self.coupon_type.id,
            "owner": self.user
        }

        request_url = self.coupon_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_coupon_fail_due_to_expired(self):
        """ 쿠폰 발급 실패 테스트 : 쿠폰 타입 만료  """

        data = {
            "type": self.coupon_type_expired.id,
            "owner": self.user
        }

        request_url = self.coupon_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_coupon_fail_due_to_inactivate(self):
        """ 쿠폰 발급 실패 테스트 : 비활성화 상태인 쿠폰 타입  """

        data = {
            "type": self.coupon_type_inactive.id,
            "owner": self.user
        }

        request_url = self.coupon_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_coupon_fail_due_to_duplicate(self):
        """ 쿠폰 발급 실패 테스트 : 중복 발급 """

        data = {
            "type": self.coupon_type_for_duplicate.id,
            "owner": self.user
        }

        request_url = self.coupon_test_url

        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
