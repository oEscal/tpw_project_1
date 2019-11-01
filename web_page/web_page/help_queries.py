from django.db.models import Q
from page.models import *


def get_all_stadium_for_team():
    already_in_team = [s['stadium__name'] for s in list(Team.objects.values('stadium__name'))]
    return Stadium.objects.filter(~Q(name__in=already_in_team)).order_by('name')


def get_all_positions():
    return Position.objects.all().order_by('id')


def get_game_team_players(game_id):
    result = {}

    for t in [s.team for s in GameStatus.objects.filter(game_id=game_id)]:
        result[t.name] = []
        for p in Player.objects.filter(team=t):
            result[t.name].append({
                'name': p.name,
                'id': p.id
            })

    return result
