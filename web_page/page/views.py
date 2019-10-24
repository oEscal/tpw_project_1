from django.contrib.auth.models import User
from django.shortcuts import render

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

    if  not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
    else:
        try:
            if request.POST:
                form = forms.Stadium(None, request.POST)
                if form.is_valid():
                    print(form.cleaned_data)
                    stadium_serializer = StadiumSerializer(data=form.cleaned_data)
                    if not stadium_serializer.is_valid():
                        error_messages = ["Campos inválidos inválidos!"]
                    else:
                        add_status, message = queries.add_stadium(stadium_serializer.data)
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
        error_messages = ["Login Invalido!"]
    else:
        try:
            if request.POST:
                form = forms.Team(None, request.POST)

                if form.is_valid():
                    print(form.cleaned_data)
                    team_serializer = TeamSerializer(data=form.cleaned_data)
                    if not team_serializer.is_valid():
                        error_messages = ["Campos inválidos"]
                    else:
                        add_status, message = queries.add_team(data=team_serializer.data)
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


def reformate_game_data(data):
    new_data = {'date': data['date'], 'journey': data['journey'], 'stadium': data['stadium']}
    new_data['teams'] = [data['home_team'], data['away_team']]
    new_data['shots'] = [data['home_shots'], data['away_shots']]
    new_data['ball_possessions'] = [data['home_ball_pos'], data['away_ball_pos']]
    new_data['corners'] = [data['home_corners'] , data['away_corners']]

    return new_data


def add_game(request):
    html_page = 'add_game.html'
    error_messages = []
    success_messages = []
    form = forms.Game()

    if verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
    else:
        try:
            if request.POST:
                form = forms.Game(None, request.POST)

                if form.is_valid():

                    game_serializer = GameSerializer(data=reformate_game_data(form.cleaned_data))

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
