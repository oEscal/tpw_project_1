from rest_framework import serializers

from page.models import *
from rest_framework.compat import MinValueValidator, MaxValueValidator


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
    picture = serializers.ImageField(required=False, allow_empty_file=True, allow_null=True)


class TeamSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    foundation_date = serializers.DateField(required=False, allow_null=True)
    logo = serializers.ImageField(required=False, allow_empty_file=True, allow_null=True)
    stadium = serializers.CharField(required=True, max_length=200)


class PlayerMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True, max_length=200)
    photo = serializers.ImageField(required=False, allow_empty_file=True, allow_null=True)


class PlayerSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    birth_date = serializers.DateField(required=True)
    photo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    nick = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=200)
    position = serializers.CharField(required=True, max_length=200)
    team = serializers.CharField(required=True, max_length=200)


class GamePlayerEventSerializer(serializers.Serializer):
    game = serializers.IntegerField(required=True, validators=[MinValueValidator(0)])
    player = serializers.IntegerField(required=True, validators=[MinValueValidator(0)])
    minute = serializers.IntegerField(required=True, validators=[MinValueValidator(0)])


class GameStatusSerializer(serializers.Serializer):
    shots = serializers.IntegerField(required=True, validators=[
        MinValueValidator(0)
    ])
    ball_possession = serializers.IntegerField(required=True, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])
    corners = serializers.IntegerField(required=True, validators=[
        MinValueValidator(0)
    ])
    goals = serializers.IntegerField(required=True, validators=[
        MinValueValidator(0)
    ])


class GameMinimalSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    journey = serializers.IntegerField(required=True, validators=[
        MaxValueValidator(MAX_JOURNEY),
        MinValueValidator(MIN_JOURNEY)
    ])
    stadium = serializers.CharField(required=True, max_length=200)


class GameSerializer(serializers.Serializer):
    # TODO -> EXTENDER DO GameSerializer
    date = serializers.DateField(required=True)
    journey = serializers.IntegerField(required=True, validators=[
        MaxValueValidator(MAX_JOURNEY),
        MinValueValidator(MIN_JOURNEY)
    ])
    stadium = serializers.CharField(required=True, max_length=200)
    teams = serializers.ListField(required=True, min_length=2, max_length=2, child=serializers.CharField(max_length=200))
    goals = serializers.ListField(required=True, min_length=2, max_length=2,
                                  child=serializers.IntegerField(validators=[MinValueValidator(0)]))
    shots = serializers.ListField(required=True, min_length=2, max_length=2,
                                  child=serializers.IntegerField(validators=[MinValueValidator(0)]))
    ball_possessions = serializers.ListField(required=True, min_length=2, max_length=2,
                                             child=serializers.IntegerField(required=True, validators=[
                                                MaxValueValidator(100),
                                                MinValueValidator(0)
                                             ]))
    corners = serializers.ListField(required=True, min_length=2, max_length=2,
                                    child=serializers.IntegerField(validators=[MinValueValidator(0)]))


class PlayerGameSerializer(serializers.Serializer):
    game = serializers.IntegerField(required=True, validators=[MinValueValidator(0)])
    player = serializers.IntegerField(required=True, validators=[MinValueValidator(0)])
