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
        return "False", "Estadio não existente!"

    try:
        Team.objects.create(name=data['name'], foundation_date=data['foundation_date'] if 'name' in data else None,
                            logo=data['logo'] if 'logo' in data else None, stadium=stadium_object[0])
        return True, "Equipa adicionada com sucesso "
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar a nova equipa!"


def add_game(data):
    try:
        # TODO -> algumas verificações pre-Jogo
        Team.objects.create(id=data['id'],
                            date=data['date'],
                            journey=data['journey'],
                            stadium=data['stadium'],
                            # team=data['team'],meter isto, so nao meti pq nao esta no serializer
                            shots=data['shots'] if 'shots' in data else None,
                            ball_possession=data['ball_possession'],
                            corners=data['corners'] if 'corners' in data else None)
        return True, "Equipa adicionada com sucesso"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar o novo jogo!"
