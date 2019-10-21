from rest_framework import serializers
from rest_framework.compat import MinValueValidator


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class StadiumSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    address = serializers.CharField(required=True, max_length=200)
    number_seats = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(0)
        ]
    )
    picture = serializers.ImageField(required=False)
