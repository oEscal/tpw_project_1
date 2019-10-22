from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_api.settings import MAX_JOURNEY, MIN_JOURNEY

# Create your models here.


class Stadium(models.Model):
    address = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)
    number_seats = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    picture = models.ImageField(null=True, blank=True)


class Team(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    foundation_date = models.DateField()
    logo = models.ImageField(null=True, blank=True)
    stadium = models.OneToOneField(Stadium, on_delete=models.CASCADE, unique=True)


class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    journey = models.IntegerField(validators=[
        MaxValueValidator(MAX_JOURNEY),
        MinValueValidator(MIN_JOURNEY)
    ])
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    team = models.ManyToManyField(Team, through='GameStatus')


class GameStatus(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
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


class Position(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    nick = models.CharField(max_length=200, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class KindEvent(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)


class Event(models.Model):
    minute = models.IntegerField(primary_key=True, validators=[
        MinValueValidator(0)
    ])


class PlayerPlayGame(models.Model):
    id = models.IntegerField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    event = models.ManyToManyField(Event)
