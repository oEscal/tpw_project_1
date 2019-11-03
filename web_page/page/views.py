import base64

from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from page.serializers import *
from web_page import queries, forms
from web_page.settings import MIN_PLAYERS_MATCH, MAX_PLAYERS_MATCH


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


def create_response(request, html_page, data=None, page_name=None, success_messages=None, error_messages=None):
    return render(request, html_page, {
        "data": data,
        "success_messages": success_messages,
        "error_messages": error_messages,
        "page_name": page_name
    })


def add_stadium(request):
    html_page = "add_stadium.html"
    page_name = "Novo Estadio"
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

    return create_response(request, html_page, data=form, page_name=page_name, error_messages=error_messages,
                           success_messages=success_messages)


def add_team(request):
    html_page = "add_team.html"
    page_name = "Nova equipa"
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

    return create_response(request, html_page, data=form, page_name=page_name,
                           error_messages=error_messages, success_messages=success_messages)


def add_player(request):
    html_page = 'add_player.html'
    page_name = "Novo jogador"
    error_messages = []
    success_messages = []
    form = forms.Player()

    if not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
        return redirect('login')
    else:
        try:
            if request.POST:
                form = forms.Player(None, request.POST, request.FILES)

                if form.is_valid():
                    data = form.cleaned_data

                    player_serializer = PlayerSerializer(data=data)
                    if not player_serializer.is_valid():
                        error_messages = ["Campos inválidos"]
                    else:
                        # encode photo
                        data['photo'] = image_to_base64(data['photo'])

                        add_status, message = queries.add_player(data=data)
                        if add_status:
                            success_messages = [message]
                        else:
                            error_messages = [message]
                else:
                    error_messages = ["Corrija os erros abaixo referidos"]

        except Exception as e:
            print(e)
            error_messages = ["Erro ao adicionar nova jogador"]

    return create_response(request, html_page, data=form, page_name=page_name,
                           error_messages=error_messages, success_messages=success_messages)


def add_players_game(request, id):
    # TODO -> se houver tempo, adicionar a verificação de se a equipa tem pelo menos 14 jogadores

    html_page = 'players_to_game.html'
    error_messages = []
    success_messages = []
    form = forms.PlayersToGame(None, id)

    if not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
        return redirect('login')
    else:
        try:
            if request.POST:
                form = forms.PlayersToGame(None, id, request.POST)

                if form.is_valid():
                    form_data = form.cleaned_data
                    data = {}
                    make_query = True

                    for p in form_data:
                        data_split = p.split('-')
                        team = data_split[0]
                        order = int(data_split[1])

                        if team not in data:
                            data[team] = []
                        if form_data[p].isdigit():
                            if form_data[p] in data[team]:
                                error_messages.append(f"Jogador {order + 1} da equipa {team} já foi escolhido!")
                                make_query = False
                            data[team].append(form_data[p])

                    # verify if number of players is greater or smaller than the constraints
                    for t in data:
                        if len(set(data[t])) > MAX_PLAYERS_MATCH or len(set(data[t])) < MIN_PLAYERS_MATCH:
                            error_messages.append(
                                f"Tem de escolher entre {MIN_PLAYERS_MATCH} e {MAX_PLAYERS_MATCH} "
                                f"jogadores na equipa {t}!"
                            )
                            make_query = False

                    if make_query:
                        add_status, message = queries.add_player_to_game({
                            'id': id,
                            'teams': data
                        })
                        if add_status:
                            success_messages = [message]
                        else:
                            error_messages = [message]
                else:
                    error_messages = ["Corrija os erros abaixo referidos"]

        except Exception as e:
            print(e)
            error_messages = ["Erro ao adicionar nova jogador"]

    form = {
        'form': form,
        'max_players': MAX_PLAYERS_MATCH,
        'min_players': MIN_PLAYERS_MATCH,
        'teams': form.teams
    }
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
        'goals': [
            data['home_goals'],
            data['away_goals']
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


def add_event(request, id):
    html_page = 'add_event.html'
    error_messages = []
    success_messages = []
    form = forms.Event(None, id)

    if not verify_if_admin(request.user):
        error_messages = ["Login inválido!"]
        return redirect('login')
    else:
        try:
            if request.POST:
                form = forms.Event(None, id, request.POST)

                if form.is_valid():
                    data = form.cleaned_data
                    if not data['players1'].isdigit() and not data['players2'].isdigit() or data['teams'] == '-':
                        error_messages = ["Tem de adicionar um jogador!"]
                    else:
                        data['game'] = id
                        data['player'] = data['players1'] if data['players1'].isdigit() else data['players2']
                        add_status, message = queries.add_event(data=data)
                        if add_status:
                            success_messages = [message]
                        else:
                            error_messages = [message]
                else:
                    error_messages = ["Corrija os erros abaixo referidos!"]

        except Exception as e:
            print(e)
            error_messages = ["Erro ao adicionar novo evento!"]

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


def games(request):
    html_page = 'games.html'
    error_messages = []
    data = []

    try:
        data, message = queries.get_games()
        if not data:
            error_messages = [message]
        print(data)
    except Exception as e:
        print(e)
        error_messages = ["Erro a obter todos os jogos"]

    return create_response(request, html_page, data=data, error_messages=error_messages)


######################### Update #########################


def update_team(request, name):
    html_page = "add_team.html"
    page_name = "Editar equipa"
    error_messages = []
    success_messages = []
    form = forms.Team()

    if not verify_if_admin(request.user):
        error_messages = ["Login invalido!"]
        return redirect('login')
    else:
        team_info, message = queries.get_minimal_team(name)

        if not team_info:
            error_messages = [message]
        else:
            form = forms.Team(team=team_info)
            try:
                if request.POST:
                    form = forms.Team(team_info, request.POST, request.FILES)

                    if form.is_valid():
                        data = form.cleaned_data

                        team_serializer = TeamSerializer(data=data)
                        if not team_serializer.is_valid():
                            error_messages = ["Campos inválidos!"]
                        else:
                            # encode logo
                            data['logo'] = image_to_base64(data['logo'])

                            add_status, message = queries.update_team(data)
                            if add_status:
                                success_messages = [message]
                            else:
                                error_messages = [message]
                    else:
                        error_messages = ["Corrija os erros abaixo referidos!"]
            except Exception as e:
                print(e)
                error_messages = ["Erro ao editar equipa!"]

    return create_response(request, html_page, data=form, page_name=page_name,
                           error_messages=error_messages, success_messages=success_messages)


def update_player(request, id):
    html_page = "add_player.html"
    page_name = "Editar jogador"
    error_messages = []
    success_messages = []
    form = forms.Player()

    if not verify_if_admin(request.user):
        error_messages = ["Login invalido!"]
        return redirect('login')
    else:
        player_info, message = queries.get_player(id)

        if not player_info:
            error_messages = [message]
        else:
            form = forms.Player(player=player_info)
            try:
                if request.POST:
                    form = forms.Player(player_info, request.POST, request.FILES)

                    if form.is_valid():
                        data = form.cleaned_data

                        player_serializer = PlayerSerializer(data=data)
                        print(data)
                        if not player_serializer.is_valid():
                            print(player_serializer.errors)
                            error_messages = ["Campos inválidos!"]
                        else:
                            # encode logo
                            data['photo'] = image_to_base64(data['photo'])
                            data['id'] = id

                            add_status, message = queries.update_player(data)
                            if add_status:
                                success_messages = [message]
                            else:
                                error_messages = [message]
                    else:
                        error_messages = ["Corrija os erros abaixo referidos!"]
            except Exception as e:
                print(e)
                error_messages = ["Erro ao editar jogador!"]

    return create_response(request, html_page, data=form, page_name=page_name,
                           error_messages=error_messages, success_messages=success_messages)


def update_stadium(request, name):
    html_page = "add_stadium.html"
    page_name = "Editar estadio"
    error_messages = []
    success_messages = []
    form = forms.Stadium()
    new_name = None
    if not verify_if_admin(request.user):
        error_messages = ["Login invalido!"]
        return redirect('login')
    else:
        stadium_info, message = queries.get_stadium(name)

        if not stadium_info:
            error_messages = [message]
        else:

            form = forms.Stadium(stadium_info)
            try:
                if request.POST:
                    form = forms.Stadium(stadium_info, request.POST, request.FILES)

                    if form.is_valid():
                        data = form.cleaned_data
                        stadium_serializer = StadiumSerializer(data=data)
                        if not stadium_serializer.is_valid():
                            error_messages = ["Campos inválidos!"]
                        else:
                            # encode logo
                            data['picture'] = image_to_base64(data['picture'])

                            data['current_name'] = stadium_info['name']

                            add_status, message = queries.update_stadium(data)
                            if add_status:
                                success_messages = [message]
                                new_name = data['name']
                            else:
                                error_messages = [message]
                    else:
                        error_messages = ["Corrija os erros abaixo referidos!"]
            except Exception as e:
                print(e)
                error_messages = ["Erro ao editar jogador!"]

    if new_name is not None:
        return redirect(f'/update_stadium/{new_name}')
    else:
        return create_response(request, html_page, data=form, page_name=page_name,
                               error_messages=error_messages, success_messages=success_messages)
