from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError
from .models import Coupon, CouponType


class CouponTypeSerializer(ModelSerializer):
    """ 쿠폰 타입 관련 시리얼라이저 """
    class Meta:
        model = CouponType
        fields = '__all__'

    def validate(self, data):
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        period = data.get('period', None)
        dc_type = data.get('dc_type', None)
        iss_type = data.get('iss_type', None)
        amount = data.get('amount', None)
        code = data.get('code', None)

        if start_date > end_date:
            raise ValidationError("ERROR: 유효 기간이 올바르지 않습니다.")

        if period < 0:
            raise ValidationError("ERROR: 유효 기한이 올바르지 않습니다.")

        if dc_type not in (0, 1, 2, 3) or iss_type not in (0, 1, 2):
            raise ValidationError("ERROR: 올바르지 않은 쿠폰 종류입니다.")

        if iss_type == 1 and not (amount and code):
            raise ValidationError("ERROR: 사용자 발급의 경우 수량과 쿠폰 코드를 지정해주세요.")

        return data


class CouponSerializer(ModelSerializer):
    pass