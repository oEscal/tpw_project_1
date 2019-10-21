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
