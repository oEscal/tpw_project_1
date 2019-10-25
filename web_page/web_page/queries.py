from django.db import transaction
from django.db.models import Max, Q

from page.serializers import *
from web_page.help_queries import get_players_per_team


def next_id(model):
    max_id = model.objects.aggregate(Max('id'))['id__max']
    if not max_id:
        max_id = 0

    return max_id + 1


######################### Add queries #########################


def add_stadium(data):
    try:
        if Stadium.objects.filter(name=data['name']).exists():
            return False, "Um estádio com o mesmo nome já existe!"

        Stadium.objects.create(
            name=data['name'], address=data['address'], number_seats=data['number_seats'],
            picture=data['picture'] if 'picture' in data else None
        )
        return True, "Estádio adicionado com sucesso"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar novo estádio!"


def add_team(data):
    try:
        stadium = data['stadium']

        if Team.objects.filter(name=data['name']).exists():
            return False, "Uma equipa com o mesmo nome já existe!"
        if Team.objects.filter(stadium__name=stadium).exists():
            return False, "Este estádio já está associado a uma equipa!"

        Team.objects.create(
            name=data['name'],
            foundation_date=data['foundation_date'] if 'foundation_date' in data else None,
            logo=data['logo'] if 'logo' in data else None,
            stadium=Stadium.objects.get(name=stadium)
        )
        return True, "Equipa adicionada com sucesso"
    except Stadium.DoesNotExist:
        return False, "Estadio não existente!"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar a nova equipa!"


def add_game(data):
    transaction.set_autocommit(False)

    try:
        # verify ball possession percentage
        if sum(data['ball_possessions']) != 100:
            return False, "A soma das posses de bola das duas equipas deve ser igual a 100!"

        new_game = Game.objects.create(
            id=next_id(Game),
            date=data['date'],
            journey=data['journey'],
            stadium=Stadium.objects.get(name=data['stadium']),
        )

        for i in range(len(data['teams'])):
            team_model = Team.objects.get(name=data['teams'][i])

            # verify if these teams already have had at least one game on that day
            if Game.objects.filter(Q(date=data['date']) & Q(team=team_model)).exists():
                return False, f"A equipa {data['teams'][i]} já jogou no referido dia!"
            if Game.objects.filter(Q(journey=data['journey']) & Q(team=team_model)):
                return False, f"A equipa {data['teams'][i]} já jogou na referida jornada!"

            players_per_team = get_players_per_team(team_model.name)

            if len(players_per_team) < 14:
                return False, f"A equipa {data['teams'][i]} não tem jogadores suficientes inscritos (minimo 14) !"

            goal_kepper_number = len(players_per_team.filter(position=Position.objects.get(id=1)))

            if goal_kepper_number < 1:
                return False, f"A equipa {data['teams'][i]} não tem o numero pelo menos 1 guarda-redes !"
            GameStatus.objects.create(
                game=new_game,
                team=team_model,
                shots=data['shots'][i],
                ball_possession=data['ball_possessions'][i],
                corners=data['corners'][i]
            )

        transaction.set_autocommit(True)
        return True, "Jogo adicionado com sucesso"
    except Team.DoesNotExist:
        transaction.rollback()
        return False, "Pelo menos uma das equipas não existe!"
    except Stadium.DoesNotExist:
        transaction.rollback()
        return False, "Estádio enexistente!"
    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro na base de dados a adicionar o novo jogo!"


def add_player(data):
    # verify is player already is on that team
    if Player.objects.filter(team__name=data['team_name'], name=data['name']):
        return False, "Ja existe um jogador com este nome na equipa!"

    try:
        Player.objects.create(
            id=next_id(Player),
            name=data['name'],
            birth_date=data['birth_date'] if 'birth_date' in data else None,
            photo=data['photo'] if 'photo' in data else None,
            nick=data['nick'] if 'nick' in data else None,
            position=Position.objects.get(name=data['position_name']),
            team=Team.objects.get(name=data['team_name'])
        )
        return True, "Jogador adicionado com sucesso"
    except Position.DoesNotExist:
        return False, "Posição escolhida não existe!"
    except Team.DoesNotExist:
        return False, "Equipa escolhida não existe!"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar um jogador!"


def add_event(data):
    transaction.set_autocommit(False)

    try:
        # verify if that player already have an event on that minute on that game
        if PlayerPlayGame.objects.filter(
                Q(player__id=data['player']) & Q(game__id=data['game']) & Q(event__minute=data['minute'])
        ).exists():
            return False, "Jogador já possui um evento nesse minuto nesse jogo!"

        new_event = Event.objects.create(
            id=next_id(Event),
            minute=data['minute']
        )

        player_play_game = PlayerPlayGame.objects.get(Q(player__id=data['player']) & Q(game__id=data['game']))
        player_play_game.event.add(new_event)

        transaction.set_autocommit(True)
        return True, "Evento adicionado com sucesso"
    except PlayerPlayGame.DoesNotExist:
        transaction.rollback()
        return False, "Este jogador não está adicionado a este jogo!"
    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro na base de dados a adicionar novo evento!"


def add_player_to_game(data):
    try:
        # verify if player is already on that game
        if PlayerPlayGame.objects.filter(Q(game__id=data['game']) & Q(player__id=data['player'])).exists():
            return False, "Jogador já adicionado a este jogo!"

        PlayerPlayGame.objects.create(
            game=Game.objects.get(id=data['game']),
            player=Player.objects.get(id=data['player'])
        )

        return True, "Jogador adicionado com sucesso ao jogo"
    except Game.DoesNotExist:
        return False, "Jogo não existente!"
    except Player.DoesNotExist:
        return False, "Jogador não existente!"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar novo jogador ao jogo"


######################### Get queries #########################


def get_teams():
    result = []

    try:
        for t in Team.objects.all():
            result.append({
                'name': t.name,
                'logo': t.logo,
            })
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter todas as equipas!"

    return result, "Sucesso"


def get_team(name):
    result = {}

    try:
        result.update(TeamSerializer(Team.objects.get(name=name)).data)

        result['stadium'] = Stadium.objects.get(team__name=name).name

        result['players'] = []
        for p in Player.objects.filter(team__name=name):
            p_info = PlayerMinimalSerializer(p).data
            p_info.update({
                'position': p.position.name
            })
            result['players'].append(p_info)
    except Team.DoesNotExist:
        return None, "Equipa não existe!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter a equipa!"

    return result, "Success"


def get_player(id):
    result = {}

    try:
        result.update(PlayerSerializer(Player.objects.get(id=id)).data)
        result['position'] = Position.objects.get(player__id=id).name
        result['team'] = Team.objects.get(player__id=id).name
    except Player.DoesNotExist:
        return None, "O jogador não existe!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter o jogador!"

    return result, "Sucesso"


def get_stadium(name):
    result = {}

    try:
        result.update(StadiumSerializer(Stadium.objects.get(name=name)).data)
        result.update({
            'team': Team.objects.get(stadium__name=name).name
        })
    except Stadium.DoesNotExist:
        return None, "Não existe nenhum estádio com esse nome na base de dados!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter o estádio!"

    return result, "Sucesso"
