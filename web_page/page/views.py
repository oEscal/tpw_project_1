import base64

from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from page.serializers import *
from web_page import queries, forms


def verify_if_admin(user):
    username = whoami(user)

    try:
        user = User.objects.get(username=username)
        if user.is_staff:
            return True
    except Exception as e:
        # when the user doesn't exist
        print(e)
        return False
    return False


def whoami(user):
    return user.username


def image_to_base64(image):
    if image:
        photo_b64 = base64.b64encode(image.file.read())
        photo_b64 = photo_b64.decode()
        return photo_b64
    return None


######################### Add #########################


def create_response(request, html_page, data=None, success_messages=None, error_messages=None):
    return render(request, html_page, {
        "data": data,
        "success_messages": success_messages,
        "error_messages": error_messages,
    })


def add_stadium(request):
    html_page = "add_stadium.html"
    error_messages = []
    success_messages = []
    form = forms.Stadium()

    if not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
        return redirect('login')
    else:
        try:
            if request.POST:
                form = forms.Stadium(None, request.POST, request.FILES)
                if form.is_valid():
                    data = form.cleaned_data
                    stadium_serializer = StadiumSerializer(data=data)
                    if not stadium_serializer.is_valid():
                        error_messages = ["Campos inválidos inválidos!"]
                    else:
                        # encode logo
                        data['picture'] = image_to_base64(data['picture'])

                        add_status, message = queries.add_stadium(data)
                        if add_status:
                            success_messages = [message]
                        else:
                            error_messages = [message]
                else:
                    error_messages = ["Corrija os erros abaixo referidos!"]
        except Exception as e:
            print(e)
            error_messages = ["Erro a adicionar novo estádio!"]

    return create_response(request, html_page, data=form, error_messages=error_messages,
                           success_messages=success_messages)


def add_team(request):
    html_page = "add_team.html"
    error_messages = []
    success_messages = []
    form = forms.Team()

    if not verify_if_admin(request.user):
        error_messages = ["Login invalido!"]
        return redirect('login')
    else:
        try:
            if request.POST:
                form = forms.Team(None, request.POST, request.FILES)

                if form.is_valid():
                    data = form.cleaned_data

                    team_serializer = TeamSerializer(data=data)
                    if not team_serializer.is_valid():
                        error_messages = ["Campos inválidos"]
                    else:
                        # encode logo

                        data['logo'] = image_to_base64(data['logo'])

                        add_status, message = queries.add_team(data=data)
                        if add_status:
                            success_messages = [message]
                        else:
                            error_messages = [message]
                else:
                    error_messages = ["Corrija os erros abaixo referidos!"]
        except Exception as e:
            print(e)
            error_messages = ["Erro ao adicionar nova equipa"]

    return create_response(request, html_page, data=form, error_messages=error_messages,
                           success_messages=success_messages)


def add_player(request):
    html_page = 'add_player.html'
    error_messages = []
    success_messages = []
    form = forms.Player()

    if not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
        return redirect('login')
    else:
        try:
            if request.POST:
                form = forms.Player(None, request.POST)

                if form.is_valid():
                    player_serializer = PlayerSerializer(data=form.cleaned_data)

                    if not player_serializer.is_valid():
                        error_messages = ["Campos inválidos"]

                    else:
                        add_status, message = queries.add_player(data=player_serializer.data)
                        if add_status:
                            success_messages = [message]
                        else:
                            error_messages = [message]
                else:
                    error_messages = ["Corrija os erros abaixo referidos"]

        except Exception as e:
            print(e)
            error_messages = ["Erro ao adicionar nova jogador"]

    return create_response(request, html_page, data=form, error_messages=error_messages,
                           success_messages=success_messages)


def reformat_game_data(data):
    new_data = {
        'date': data['date'],
        'journey': data['journey'],
        'stadium': data['stadium'],
        'teams': [
            data['home_team'],
            data['away_team']
        ],
        'shots': [
            data['home_shots'],
            data['away_shots']
        ],
        'ball_possessions': [
            data['home_ball_pos'],
            data['away_ball_pos']
        ],
        'corners': [
            data['home_corners'],
            data['away_corners']
        ]
    }

    return new_data


def add_game(request):
    html_page = 'add_game.html'
    error_messages = []
    success_messages = []
    form = forms.Game()

    if not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
        return redirect('login')
    else:
        try:
            if request.POST:
                form = forms.Game(None, request.POST)

                if form.is_valid():

                    game_serializer = GameSerializer(data=reformat_game_data(form.cleaned_data))

                    if not game_serializer.is_valid():
                        error_messages = ["Campos inválidos!"]
                    else:
                        add_status, message = queries.add_game(data=game_serializer.data)

                        if add_status:
                            success_messages = [message]
                        else:
                            error_messages = [message]
                else:
                    error_messages = ["Corrija os erros abaixo referidos"]

        except Exception as e:
            print(e)
            error_messages = ["Erro ao adicionar novo jogo"]

    return create_response(request, html_page, data=form, error_messages=error_messages,
                           success_messages=success_messages)


######################### Get #########################


def teams(request):
    html_page = 'teams.html'
    error_messages = []
    data = []

    try:
        data, message = queries.get_teams()
        if not data:
            error_messages = [message]
    except Exception as e:
        print(e)
        error_messages = ["Erro a obter todas as equipas!"]

    return create_response(request, html_page, data=data, error_messages=error_messages)


def team(request, name):
    html_page = 'team.html'
    error_messages = []
    data = {}

    try:
        data, message = queries.get_team(name)
        if not data:
            error_messages = [message]
    except Exception as e:
        print(e)
        error_messages = ["Erro a obter a equipa!"]

    return create_response(request, html_page, data=data, error_messages=error_messages)


def player(request, id):
    html_page = 'player.html'
    error_messages = []
    data = []

    try:
        data, message = queries.get_player(id)
        if not data:
            error_messages = [message]
    except Exception as e:
        print(e)
        error_messages = ["Erro a obter o jogador!"]

    return create_response(request, html_page, data=data, error_messages=error_messages)


def stadium(request, name):
    html_page = 'stadium.html'
    error_messages = []
    data = []

    try:
        data, message = queries.get_stadium(name)
        if not data:
            error_messages = [message]

    except Exception as e:
        print(e)
        error_messages = ["Erro a obter o estádio!"]

    return create_response(request, html_page, data=data, error_messages=error_messages)
