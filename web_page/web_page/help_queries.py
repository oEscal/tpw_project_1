from django.db.models import Q

from page.models import *
from web_page.queries import *


def get_all_stadium_for_team(except_stadium):
    already_in_team = [s['stadium__name'] for s in list(Team.objects.values('stadium__name'))]
    if except_stadium:
        already_in_team.remove(except_stadium)
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


def get_all_stadium():
    return Stadium.objects.all()


def get_all_teams():
    return Team.objects.all()


def get_info_for_add_event(game_id=None, event_id=None):
    result = {
        'teams': {}
    }

    if not event_id:
        player_game = PlayerPlayGame.objects.filter(game_id=game_id)
    else:
        player_game = PlayerPlayGame.objects.filter(
            game=PlayerPlayGame.objects.get(event__id=event_id).game
        )
    for p in player_game:
        player = p.player
        team = player.team.name
        if team not in result['teams']:
            result['teams'][team] = []
        result['teams'][team].append({
            'id': player.id,
            'name': player.name
        })


def get_info_for_add_event(game_id):
    result = {
        'teams': get_players_per_game(game_id)[0],
        'events': [k.name for k in KindEvent.objects.all()]
    }

    return result
