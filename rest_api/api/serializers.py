from rest_framework import serializers

from api.models import *


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


class TeamSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    foundation_date = serializers.DateField(required=False)
    logo = serializers.ImageField(required=False)
    stadium_name = serializers.CharField(required=True, max_length=200)


class PlayerSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    birth_date = serializers.DateField(required=False)
    photo = serializers.ImageField(required=False)
    nick = serializers.CharField(required=False, max_length=200)
    position_name = serializers.CharField(required=True, max_length=200)
    team_name = serializers.CharField(required=True, max_length=200)


