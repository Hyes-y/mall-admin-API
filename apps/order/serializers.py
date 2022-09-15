from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import Order
from apps.coupon.models import Coupon
from apps.utils import get_current_date, get_exchange_rate, get_delivery_cost


class OrderSerializer(serializers.ModelSerializer):
    """
    주문 내역 조회, 수정, 삭제 시리얼라이저
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
        ! `결제 취소` 로 수정시 쿠폰 적용 리셋
        pay_state: 0(결제 취소), 1(결제 대기), 2(결제 완료)
        delivery_state: 0(배송 취소), 1(배송 준비중), 2(배송 중), 3(배송 완료)
        """
        pay_state = validated_data.get('pay_state', instance.pay_state)
        delivery_state = validated_data.get('delivery_state', instance.delivery_state)

        # 수정 사항 반영
        instance.pay_state = pay_state
        instance.delivery_state = delivery_state
        instance.save()

        # 결제 취소로 변경하는 경우 쿠폰 사용 초기화
        if pay_state == 0 and instance.coupon:
            coupon = Coupon.objects.get(owner=instance.user,
                                        code=instance.coupon)
            coupon.is_used = False
            coupon.date = None
            coupon.sale_amount = None
            coupon.save()

        return instance


class OrderTestSerializer(serializers.ModelSerializer):
    """
    주문 내역 생성 시리얼라이저 (테스트용)
    """
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        """ 주문 내역 생성시 쿠폰 반영 """
        user = validated_data.get('user', None)
        quantity = validated_data.get('quantity', None)
        price = validated_data.get('price', None)
        coupon_code = validated_data.get('coupon', None)
        country = validated_data.get('buyr_country', None)

        # 결제 상태, 배송 상태 디폴트로 설정
        validated_data['pay_state'] = 1
        validated_data['delivery_state'] = 1

        # 국가별, 개수별 배송비 가져오기
        delivery_cost = get_delivery_cost(country, quantity)

        # 환율 정보(원화의 경우 1)
        exchange_rate = 1

        # 해외 주문의 경우 달러 가격 원화로 변경
        if country != "KR":
            exchange_rate = get_exchange_rate()
            price *= exchange_rate

        payment_amount = price * quantity

        # 할인 금액
        dc_amount = 0

        # 유효한 쿠폰인지 확인
        coupon = Coupon.objects.filter(
                        owner=user,
                        code=coupon_code,
                        is_expired=False,
                        is_used=False,
                        expired_date__gte=get_current_date())

        if len(coupon) == 0:
            raise ValidationError("ERROR: 유효하지 않은 쿠폰입니다.")

        coupon = coupon[0]

        if payment_amount < coupon.type.min_price:
            raise ValidationError(f"ERROR: 주문 금액이 {coupon.type.min_price} 이상이어야 해당 쿠폰 사용이 가능합니다.")

        # 쿠폰 적용 로직
        # 1) 배송비 할인
        if coupon.type.dc_type == 0:
            dc_amount = delivery_cost
            delivery_cost = 0
        # 2) 퍼센트 할인 (단, 할인 금액이 해당 쿠폰 타입의 최대 할인 금액 이상인 경우 최대 할인 금액만큼만 할인)
        elif coupon.type.dc_type == 1:
            if payment_amount * (coupon.type.value / 100) <= coupon.type.max_dc_price:
                dc_amount = payment_amount * (coupon.type.value / 100)
            else:
                dc_amount = coupon.type.max_dc_price
        # 3) 정액 할인 (KRW 원화 기준)
        elif coupon.type.dc_type == 2:
            dc_amount = min(coupon.type.value, payment_amount)

        sale_price = payment_amount - dc_amount
        payment_amount = sale_price + delivery_cost

        validated_data['delivery_cost'] = delivery_cost * exchange_rate
        validated_data['sale_price'] = sale_price * exchange_rate
        validated_data['payment_amount'] = payment_amount * exchange_rate

        try:
            order = self.Meta.model.objects.create(**validated_data)
        except:
            raise ValidationError("ERROR: 유효하지 않은 주문입니다.")

        # 쿠폰 사용 처리
        coupon.is_used = True
        coupon.sale_amount = dc_amount
        coupon.date = get_current_date()
        coupon.save()

        return order


