from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_api.settings import MAX_JOURNEY, MIN_JOURNEY


# Create your models here.


class Stadium(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    number_seats = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    picture = models.ImageField(null=True, blank=True)


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    foundation_date = models.DateField()
    logo = models.ImageField(null=True, blank=True)
    stadium = models.OneToOneRel(Stadium)


class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    journey = models.IntegerField(validators=[
        MaxValueValidator(MAX_JOURNEY),
        MinValueValidator(MIN_JOURNEY)
    ])
    stadium = models.ManyToOneRel(Stadium)
    team = models.ManyToManyField(Team)
    shots = models.IntegerField(validators=[
        MinValueValidator(0)
    ])
    ball_possession = models.IntegerField(validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])
    corners = models.IntegerField(validators=[
        MinValueValidator(0)
    ])

class Player_position(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)
    birth_data = models.DateField(blank=True)
    photo = models.TextField(blank=True)
    nick = models.CharField(max_length=1000, blank=True)
    position_id = models.ForeignKey(Player_position)
    team = models.ManyToManyField(Team)


class Player_function(object):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)

class Player_play_game(models.Model):
    player_id = models.ForeignKey(Player, primary_key=True)
    game_id = models.ForeignKey(Game, primary_key=True)
    function_id = models.ForeignKey(Player_function, primary_key=True)


class Kind_event(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)


class Event(models.Model):
    minute = models.IntegerField(primary_key=True)
    player_id = models.ForeignKey(Player, primary_key=True)
    game_id = models.ForeignKey()
    event_id = models.ForeignKey(Kind_event)

