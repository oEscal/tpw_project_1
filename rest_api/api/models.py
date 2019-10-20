from django.db import models


# Create your models here.
class Player_position(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)


class Stadium(object):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000, unique=True)
    address = models.CharField(max_length=1000, unique=True)
    spot_numbers = models.IntegerField()  # Fazer o check???


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000, unique=True)
    creation_data = models.DateField(blank=True)
    stadium_id = models.ForeignKey(Stadium)
    logo = models.TextField(blank=True)


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)
    birth_data = models.DateField(blank=True)
    photo = models.TextField(blank=True)
    nick = models.CharField(max_length=1000, blank=True)
    position_id = models.ForeignKey(Player_position)
    team = models.ManyToManyField(Team)


class Game(object):
    pass


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
