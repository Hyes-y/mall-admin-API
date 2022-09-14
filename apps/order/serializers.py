from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import Order
from apps.coupon.models import Coupon
from apps.utils import get_current_date, get_dollar, get_delivery_cost


class OrderSerializer(serializers.ModelSerializer):
    """
    주문 내역 조회, 수정 시리얼라이저
    수정 가능 필드: 'pay_state', 'delivery_state'
    """
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'user', 'date', 'quantity',
                            'price', 'sale_price', 'delivery_cost',
                            'payment_amount', 'coupon',
                            'buyr_city', 'buyr_zips', 'vccode']

    def validate(self, data):
        pay_state = data.get('pay_state', None)
        delivery_state = data.get('delivery_state', None)

        if pay_state and pay_state not in (0, 1, 2):
            raise ValidationError("ERROR: 올바르지 않은 결제 상태입니다.")
        elif delivery_state and delivery_state not in (0, 1, 2, 3):
            raise ValidationError("ERROR: 올바르지 않은 배송 상태입니다.")
        return data

    def update(self, instance, validated_data):
        """
        주문 내역 수정 함수
        pay_state: 0(결제 취소), 1(결제 대기), 2(결제 완료)
        delivery_state: 0(배송 취소), 1(배송 준비중), 2(배송 중), 3(배송 완료)
        """
        pay_state = validated_data.get('pay_state', instance.pay_state)
        delivery_state = validated_data.get('delivery_state', instance.delivery_state)

        # 결제 취소로 변경하는 경우 쿠폰 사용 초기화
        if pay_state == 0 and instance.coupon:
            coupon = Coupon.objects.get(owner=instance.user,
                                        code=instance.coupon)
            coupon.is_used = False
            coupon.date = None
            coupon.sale_amount = None
            coupon.save()

        instance.pay_state = pay_state
        instance.delivery_state = delivery_state
        instance.save()

        return instance


class OrderTestSerializer(serializers.ModelSerializer):
    """
    주문 내역 생성 시리얼라이저 (테스트용)
    """
    class Meta:
        model = Order
        fields = '__all__'
        # read_only_fields = ['id', 'date', 'updated_at', 'sale_price',
        #                     'delivery_cost', 'payment_amount', 'pay_state',
        #                     'delivery_state', 'delivery_num']

    def create(self, validated_data):
        user = validated_data.get('user', None)
        quantity = validated_data.get('quantity', None)
        price = validated_data.get('price', None)
        coupon_code = validated_data.get('coupon', None)
        buyr_country = validated_data.get('buyr_country', None)

        validated_data['pay_state'] = 1
        validated_data['delivery_state'] = 1
        delivery_cost = get_delivery_cost(buyr_country, quantity)
        payment_amount = price * quantity
        dc_amount = 0

        coupon = Coupon.objects.filter(
                        owner=user,
                        code=coupon_code,
                        is_expired=False,
                        is_used=False,
                        expired_date__gte=get_current_date())

        if len(coupon) == 0 or payment_amount < coupon[0].type.min_price:
            raise ValidationError("ERROR: 유효하지 않은 쿠폰입니다.")

        coupon = coupon[0]

        if coupon.type.dc_type == 0:
            dc_amount = delivery_cost
            delivery_cost = 0
        elif coupon.type.dc_type == 1:
            if payment_amount * (coupon.type.value / 100) <= coupon.type.max_dc_price:
                dc_amount = payment_amount * (coupon.type.value / 100)
            else:
                dc_amount = coupon.type.max_dc_price

        elif coupon.type.dc_type == 2:
            if buyr_country == "KR":
                dc_amount = coupon.type.value
            else:
                dc_amount = get_dollar(coupon.type.value)

        sale_price = payment_amount - dc_amount
        payment_amount = sale_price + delivery_cost

        validated_data['delivery_cost'] = delivery_cost
        validated_data['sale_price'] = sale_price
        validated_data['payment_amount'] = payment_amount

        # 쿠폰 사용 처리
        coupon.is_used = True
        coupon.sale_amount = dc_amount
        coupon.date = get_current_date()
        coupon.save()

        return self.Meta.model.objects.create(**validated_data)


