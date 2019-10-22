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
    position = Position.objects.filter(name=data['position_name'])
    if not position.exists():  # verificar se a posição escolhida existe
        return False, "Posição escolhida não existe!"

    team = Team.objects.filter(name=data['team_name'])
    if not team.exists():  # verificar se a equipa escolhida existe
        return False, "Equipa escolhida não existe!"

    if Player.objects.filter(team=team[0], name=data[
        'name']):  # verificar se o nome selecionado para o jogador já nao se encontra na equipa
        return False, "Ja existe um jogador come este nome na equipa!"

    try:
        Player.objects.create(
            id=next_id(Player),
            name=data['name'],
            birth_date=data['birth_date'] if 'birth_date' in data else None,
            photo=data['photo'] if 'photo' in data else None,
            nick=data['nick'] if 'nick' in data else None,
            position=position[0],
            team=team[0]
        )
        return True, "Jogador adicionado com sucesso"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar um jogador"
