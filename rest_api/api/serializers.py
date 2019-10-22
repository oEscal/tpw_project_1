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


class GameSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    journey = serializers.IntegerField(required=True, validators=[
        MaxValueValidator(MAX_JOURNEY),
        MinValueValidator(MIN_JOURNEY)
    ])
    stadium = serializers.CharField(required=True, max_length=200)
    team = serializers.ListField(required=True, min_length=2, max_length=2, child=serializers.CharField())
    shots = serializers.IntegerField(validators=[MinValueValidator(0)])
    ball_possession = serializers.IntegerField(required=True, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])
    corners = serializers.IntegerField(validators=[MinValueValidator(0)])
