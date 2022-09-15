from rest_framework import status
from rest_framework.test import APITestCase

from apps.coupon.models import Coupon, CouponType
from apps.utils import get_current_date, add_period, code_generator


class OrderTest(APITestCase):
    """
    주문 (쿠폰 적용) 테스트
    """
    def setUp(self):
        """ test 를 위한 mock 데이터 추가 """
        self.order_test_url = "/api/v1/admin/orders/test/"
        self.user = 1

        self.coupon_type = CouponType.objects.create(
            start_date="2022-09-13 00:00:00",
            end_date="2022-09-16 00:00:00",
            period=7,
            min_price=50000,
            max_dc_price=15000,
            dc_type=0,
            iss_type=0,
            description="배송비 할인 쿠폰"
        )

        self.coupon_success = Coupon.objects.create(
            type=self.coupon_type,
            expired_date=add_period(get_current_date(), self.coupon_type.period),
            is_used=False,
            owner=self.user,
            code=code_generator(1)
        )

        self.coupon_fail_min_price = Coupon.objects.create(
            type=self.coupon_type,
            expired_date=add_period(get_current_date(), self.coupon_type.period),
            is_used=False,
            owner=self.user,
            code=code_generator(1)
        )

        self.coupon_fail_expired = Coupon.objects.create(
            type=self.coupon_type,
            expired_date=add_period(get_current_date(), self.coupon_type.period),
            is_used=False,
            owner=self.user,
            code=code_generator(1),
            is_expired=True
        )

        self.data = {
            "user": self.user,
            "quantity": 3,
            "price": 50,
            "coupon": "1",
            "buyr_city": "otawa",
            "buyr_country": "CA",
            "buyr_zipx": "1",
            "vccode": "1",
            "delivery_num": 1
        }

    def test_order_success(self):
        """ 주문 성공 테스트 """

        self.data['coupon'] = self.coupon_success.code
        request_url = self.order_test_url

        response = self.client.post(request_url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_order_fail_due_to_price(self):
        """ 주문 실패 테스트 : 최소 주문 금액보다 적은 경우 """

        self.data['coupon'] = self.coupon_fail_min_price.code
        self.data['price'] = 15000
        self.data['buyr_city'] = 'Seoul'
        self.data['buyr_country'] = "KR"

        request_url = self.order_test_url

        response = self.client.post(request_url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_fail_due_to_expired(self):
        """ 주문 실패 테스트 : 쿠폰이 만료된 경우 """

        self.data['coupon'] = self.coupon_fail_expired.code
        self.data['price'] = 45000
        self.data['buyr_city'] = 'Seoul'
        self.data['buyr_country'] = "KR"

        request_url = self.order_test_url

        response = self.client.post(request_url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

