import base64

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

    if not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
    else:
        try:
            if request.POST:
                form = forms.Stadium(None, request.POST)
                if form.is_valid():
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
        error_messages = ["Login invalido!"]
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
                        if data['logo']:
                            photo_b64 = base64.b64encode(data["logo"].file.read())
                            photo_b64 = photo_b64.decode()
                            data["logo"] = photo_b64
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

    if  verify_if_admin(request.user):
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
