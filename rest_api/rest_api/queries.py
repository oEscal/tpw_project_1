from django.db.models import Max

from api.models import *


def next_id(model):
    max_id = model.objects.aggregate(Max('id'))['id__max']
    if not max_id:
        max_id = 0

    return max_id + 1


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
    stadium_name = data['stadium_name']
    stadium_object = Stadium.objects.filter(name=stadium_name)

    if not stadium_object.exists():
        return False, "Estadio não existente!"

    if Team.objects.filter(name=data['name']).exists():
        return False, "Uma equipa com o mesmo nome já existe!"

    if Team.objects.filter(stadium__name=stadium_name).exists():
        return False, "Este estádio já está associado a uma equipa!"

    try:
        Team.objects.create(name=data['name'],
                            foundation_date=data['foundation_date'] if 'foundation_date' in data else None,
                            logo=data['logo'] if 'logo' in data else None, stadium=stadium_object[0])
        return True, "Equipa adicionada com sucesso"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar a nova equipa!"


def add_player(data):
    # verify is player already is on that team
    if Player.objects.filter(team__name=data['team_name'], name=data['name']):
        return False, "Ja existe um jogador come este nome na equipa!"

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
        return False, "Erro na base de dados a adicionar um jogador"
