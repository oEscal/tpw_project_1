from django.db.models import Q
from page.models import *


def get_all_stadium_for_team():
    already_in_team = [s['stadium__name'] for s in list(Team.objects.values('stadium__name'))]
    return Stadium.objects.filter(~Q(name__in=already_in_team)).order_by('name')


def get_all_positions():
    return Position.objects.all().order_by('id')


def get_all_stadium():
    return Stadium.objects.all()


def get_players_per_team(team_name):
    return Player.objects.filter(team__name=team_name).all()


def get_all_teams():
    return Team.objects.all()


def get_info_for_add_event(game_id):
    result = {}

    for p in PlayerPlayGame.objects.filter(game_id=game_id):
        player = p.player
        team = player.team.name
        if team not in result:
            result[team] = []
        result[team].append({
            'id': player.id,
            'name': player.name
        })

    result['events'] = [k.name for k in KindEvent.objects.all()]

    return result
