from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import *

import rest_api.queries as queries
from api.serializers import *


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


def create_response(message, status, token=None, data=None):
    return Response({
        "message": message,
        "data": data,
        "token": token,
    }, status=status)


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    if not login_serializer.is_valid():
        return create_response("Dados inválidos!", HTTP_404_NOT_FOUND, data=login_serializer.errors)

    user = authenticate(
        username=login_serializer.data['username'],
        password=login_serializer.data['password']
    )

    if not user:
        message = "Login inválido!"
        return create_response(message, HTTP_404_NOT_FOUND)

    # TOKEN STUFF
    token, _ = Token.objects.get_or_create(user=user)

    return create_response("Login feito com sucesso", HTTP_200_OK, token=token.key)


@csrf_exempt
@api_view(["POST"])
def add_stadium(request):
    if not verify_if_admin(request.user):
        return create_response("Login inválido!", HTTP_401_UNAUTHORIZED)

    token = Token.objects.get(user=request.user).key
    try:
        stadium_serializer = StadiumSerializer(data=request.data)
        if not stadium_serializer.is_valid():
            return create_response("Dados inválidos!", HTTP_400_BAD_REQUEST, token=token,
                                   data=stadium_serializer.errors)

        add_status, message = queries.add_stadium(stadium_serializer.data)
        return create_response(message, HTTP_200_OK if add_status else HTTP_404_NOT_FOUND, token=token)
    except Exception as e:
        print(e)
        return create_response("Erro a adicionar novo estádio!", HTTP_403_FORBIDDEN, token=token)


@csrf_exempt
@api_view(["POST"])
def add_team(request):
    if not verify_if_admin(request.user):
        return create_response("Login inválido!", HTTP_401_UNAUTHORIZED)

    token = Token.objects.get(user=request.user).key
    try:
        team_serializer = TeamSerializer(data=request.data)
        if not team_serializer.is_valid():
            return create_response("Dados inválidos!", HTTP_400_BAD_REQUEST, token=token, data=team_serializer.errors)

        add_status, message = queries.add_team(team_serializer.data)
        return create_response(message, HTTP_200_OK if add_status else HTTP_404_NOT_FOUND, token=token)
    except Exception as e:
        print(e)
        return create_response("Erro a adicionar nova equipa!", HTTP_403_FORBIDDEN, token=token)


@csrf_exempt
@api_view(["POST"])
def add_player(request):
    if not verify_if_admin(request.user):
        return create_response("Login inválido!", HTTP_401_UNAUTHORIZED)

    token = Token.objects.get(user=request.user).key
    try:
        player_serializer = PlayerSerializer(data=request.data)
        if not player_serializer.is_valid():
            return create_response("Dados inválidos!", HTTP_400_BAD_REQUEST, token=token, data=player_serializer.errors)

        add_status, message = queries.add_player(player_serializer.data)
        return create_response(message, HTTP_200_OK if add_status else HTTP_404_NOT_FOUND, token=token)
    except Exception as e:
        print(e)
        return create_response("Erro ao adicionar jogador!", HTTP_403_FORBIDDEN, token=token)


@csrf_exempt
@api_view(["POST"])
def add_event(request):
    if not verify_if_admin(request.user):
        return create_response("Login inválido!", HTTP_401_UNAUTHORIZED)

    token = Token.objects.get(user=request.user).key
    try:
        event_serializer = GamePlayerEventSerializer(data=request.data)
        if not event_serializer.is_valid():
            return create_response(
                "Dados inválidos!",
                HTTP_400_BAD_REQUEST,
                token=token,
                data=event_serializer.errors
            )

        add_status, message = queries.add_event(event_serializer.data)
        return create_response(message, HTTP_200_OK if add_status else HTTP_404_NOT_FOUND, token=token)
    except Exception as e:
        print(e)
        return create_response("Erro ao adicionar jogador!", HTTP_403_FORBIDDEN, token=token)


@csrf_exempt
@api_view(["POST"])
def add_game(request):
    if not verify_if_admin(request.user):
        return create_response("Login inválido!", HTTP_401_UNAUTHORIZED)

    token = Token.objects.get(user=request.user).key
    try:
        game_serializer = GameSerializer(data=request.data)
        if not game_serializer.is_valid():
            return create_response("Dados inválidos!", HTTP_400_BAD_REQUEST, token=token,
                                   data=game_serializer.errors)

        add_status, message = queries.add_game(game_serializer.data)
        return create_response(message, HTTP_200_OK if add_status else HTTP_404_NOT_FOUND, token=token)
    except Exception as e:
        print(e)
        return create_response("Erro a adicionar jogo!", HTTP_403_FORBIDDEN, token=token)


@csrf_exempt
@api_view(["POST"])
def add_player_to_game(request):
    if not verify_if_admin(request.user):
        return create_response("Login inválido!", HTTP_401_UNAUTHORIZED)

    token = Token.objects.get(user=request.user).key
    try:
        player_game_serializer = PlayerGameSerializer(data=request.data)
        if not player_game_serializer.is_valid():
            return create_response("Dados inválidos!", HTTP_400_BAD_REQUEST, token=token,
                                   data=player_game_serializer.errors)

        add_status, message = queries.add_player_to_game(player_game_serializer.data)
        return create_response(message, HTTP_200_OK if add_status else HTTP_404_NOT_FOUND, token=token)
    except Exception as e:
        print(e)
        return create_response("Erro a adicionar jogador ao jogo!", HTTP_403_FORBIDDEN, token=token)
