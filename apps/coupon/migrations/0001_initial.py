# Generated by Django 4.1 on 2022-09-14 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CouponType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(null=True, verbose_name='유효기간(시작)')),
                ('end_date', models.DateTimeField(null=True, verbose_name='유효기간(종료)')),
                ('period', models.PositiveIntegerField(null=True, verbose_name='유효기간(기한)')),
                ('min_price', models.PositiveIntegerField(null=True, verbose_name='조건(최소금액)')),
                ('max_dc_price', models.PositiveIntegerField(null=True, verbose_name='조건(최대할인금액)')),
                ('dc_type', models.PositiveIntegerField(choices=[(0, '배송비 할인'), (1, '퍼센트(%) 할인'), (2, '정액 할인(KRW)'), (3, '정액 할인(USD)')], verbose_name='타입(할인종류)')),
                ('iss_type', models.PositiveIntegerField(choices=[(0, '지정 발급'), (1, '사용자 발급'), (2, '자동 발급')], verbose_name='타입(발급종류)')),
                ('value', models.PositiveIntegerField(null=True, verbose_name='값')),
                ('description', models.CharField(max_length=30, verbose_name='설명')),
                ('amount', models.PositiveIntegerField(null=True, verbose_name='수량')),
                ('code', models.CharField(max_length=20, null=True, verbose_name='쿠폰 코드')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateField(auto_now_add=True, verbose_name='발급 날짜')),
                ('expired_date', models.DateField(verbose_name='만료 날짜')),
                ('is_used', models.BooleanField(default=False, verbose_name='사용 여부')),
                ('date', models.DateTimeField(null=True, verbose_name='사용 날짜')),
                ('sale_amount', models.PositiveIntegerField(null=True, verbose_name='할인금액')),
                ('owner', models.PositiveIntegerField(blank=True, null=True, verbose_name='소유자')),
                ('code', models.CharField(max_length=20, verbose_name='발급 코드')),
                ('is_expired', models.BooleanField(default=False, verbose_name='만료 여부')),
                ('type', models.ForeignKey(db_column='type', on_delete=django.db.models.deletion.DO_NOTHING, to='coupon.coupontype')),
            ],
        ),
    ]
