from django.db import transaction
from django.db.models import Max, Q

from api.serializers import *
from rest_api.settings import MAX_PLAYERS_MATCH, MIN_PLAYERS_MATCH


def next_id(model):
    max_id = model.objects.aggregate(Max('id'))['id__max']
    if not max_id:
        max_id = 0

    return max_id + 1


def get_players_per_team(team_name):
    return Player.objects.filter(team__name=team_name).all()


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
            transaction.rollback()
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
            if Game.objects.filter(Q(date=data['date']) & Q(gamestatus__team=team_model)).exists():
                transaction.rollback()
                return False, f"A equipa {data['teams'][i]} já jogou no referido dia!"
            if Game.objects.filter(Q(journey=data['journey']) & Q(gamestatus__team=team_model)):
                transaction.rollback()
                return False, f"A equipa {data['teams'][i]} já jogou na referida jornada!"

            players_per_team = get_players_per_team(team_model.name)

            if len(players_per_team) < 14:
                transaction.rollback()
                return False, f"A equipa {data['teams'][i]} não tem jogadores suficientes inscritos (minimo 14) !"

            goal_keeper_number = len(players_per_team.filter(position=Position.objects.get(id=1)))

            if goal_keeper_number < 1:
                transaction.rollback()
                return False, f"A equipa {data['teams'][i]} não tem o numero pelo menos 1 guarda-redes!"

            GameStatus.objects.create(
                game=new_game,
                team=team_model,
                goals=data['goals'][i],
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
        print(e)
        transaction.rollback()
        return False, "Erro na base de dados a adicionar o novo jogo!"


def add_player(data):
    # verify is player already is on that team
    if Player.objects.filter(team__name=data['team'], name=data['name']):
        return False, "Ja existe um jogador com este nome na equipa!"

    try:
        Player.objects.create(
            id=next_id(Player),
            name=data['name'],
            birth_date=data['birth_date'] if 'birth_date' in data else None,
            photo=data['photo'] if 'photo' in data else None,
            nick=data['nick'] if 'nick' in data else None,
            position=Position.objects.get(name=data['position']),
            team=Team.objects.get(name=data['team'])
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
            minute=data['minute'],
            kind_event=KindEvent.objects.get(name=data['kind_event'])
        )

        player_play_game = PlayerPlayGame.objects.get(Q(player__id=data['player']) & Q(game__id=data['game']))
        player_play_game.event.add(new_event)

        transaction.set_autocommit(True)
        return True, "Evento adicionado com sucesso"
    except KindEvent.DoesNotExist:
        transaction.rollback()
        return False, "Esse evento não existe!"
    except PlayerPlayGame.DoesNotExist:
        transaction.rollback()
        return False, "Este jogador não está adicionado a este jogo!"
    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro na base de dados a adicionar novo evento!"


def add_player_to_game(data):
    transaction.set_autocommit(False)

    try:
        game_id = data['id']
        teams = data['teams']

        # verify max and min number of players on that team on that game
        for t in teams:
            if len(set(teams[t])) > MAX_PLAYERS_MATCH or len(set(teams[t])) < MIN_PLAYERS_MATCH:
                return False, f"O número de jogadores por equipa deve estar compreendido " \
                              f"entre {MIN_PLAYERS_MATCH} e {MAX_PLAYERS_MATCH}!"

        # verify if already there are players on that game
        if PlayerPlayGame.objects.filter(game_id=game_id).exists():
            return False, "Já foram definidos os jogadores que jogam nesse jogo!"

        for t in teams:
            for p in teams[t]:
                PlayerPlayGame.objects.create(
                    game=Game.objects.get(id=game_id),
                    player=Player.objects.get(id=p)
                )

        transaction.set_autocommit(True)
        return True, "Jogador adicionado com sucesso ao jogo"
    except Game.DoesNotExist:
        transaction.rollback()
        return False, "Jogo não existente!"
    except Player.DoesNotExist:
        transaction.rollback()
        return False, "Jogador não existente!"
    except Exception as e:
        print(e)
        transaction.rollback()
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


def get_minimal_team(name):
    result = {}

    try:
        team = Team.objects.get(name=name)
        result.update(TeamSerializer(team).data)
        result['logo'] = team.logo

        result['stadium'] = Stadium.objects.get(team__name=name).name
    except Team.DoesNotExist:
        return None, "Equipa não existe!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter a equipa!"

    return result, "Sucesso"


def get_team(name):
    result = {}

    try:
        data, message = get_minimal_team(name)
        if data:
            result.update(data)
        else:
            return data, message

        result['players'] = []
        for p in Player.objects.filter(team__name=name).order_by('position__id'):
            p_info = PlayerMinimalSerializer(p).data
            p_info['photo'] = p.photo
            p_info.update({
                'position': p.position.name
            })
            result['players'].append(p_info)
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter os jogadores da equipa!"

    return result, "Sucesso"


def get_player(id):
    result = {}

    try:
        player = Player.objects.get(id=id)
        result.update(PlayerSerializer(player).data)

        result['photo'] = player.photo
        result['position'] = Position.objects.get(player__id=id).name
        result['team'] = Team.objects.get(player__id=id).name
        result['id'] = id
    except Player.DoesNotExist:
        return None, "O jogador não existe!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter o jogador!"

    return result, "Sucesso"


def get_stadium(name):
    result = {}

    try:
        stadium = Stadium.objects.get(name=name)

        result.update(StadiumSerializer(stadium).data)
        result.update({
            'team': Team.objects.get(stadium__name=name).name
        })
        result['picture'] = stadium.picture
    except Stadium.DoesNotExist:
        return None, "Não existe nenhum estádio com esse nome na base de dados!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter o estádio!"

    return result, "Sucesso"


def get_games():
    result = []

    try:
        for g in Game.objects.all().order_by('date'):
            current_game = GameMinimalSerializer(g).data
            current_game['id'] = g.id
            current_game['stadium'] = g.stadium.name
            current_game['stadium_picture'] = g.stadium.picture

            current_game['teams'] = []
            for stat in GameStatus.objects.filter(game=g):
                current_info = {
                    'name': stat.team.name,
                    'logo': stat.team.logo
                }
                current_info.update(GameStatusSerializer(stat).data)
                current_game['teams'].append(current_info)

            current_game['events'] = []

            for event in Event.objects.filter(playerplaygame__game__id=g.id).order_by('minute'):
                pg = PlayerPlayGame.objects.get(event=event)
                current_game['events'].append({
                    'kind_event': event.kind_event.name,
                    'id': event.id,
                    'minute': event.minute,
                    'player': pg.player.name,
                    'player_id': pg.player.id,
                    'photo': pg.player.photo,
                    'team': pg.player.team.name
                })

            result.append(current_game)
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter todos os jogos!"

    return result, "Sucesso"


def get_minimal_event(id):
    try:
        pg = PlayerPlayGame.objects.get(event__id=id)
        event = Event.objects.get(id=id)
        result = {
            'id': id,
            'team': pg.player.team.name,
            'player': pg.player.id,
            'kind_event': event.kind_event.name,
            'minute': event.minute
        }
        return result, "Sucesso"
    except PlayerPlayGame.DoesNotExist:
        return None, "Não existe nenhum jogador atribuido a esse evento!"
    except Event.DoesNotExist:
        return None, "Esse evento não existe!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter o evento!"


######################### Update #########################


def get_players_per_game(game_id, event_id=None):
    result = {}

    if not event_id:
        player_game = PlayerPlayGame.objects.filter(game_id=game_id)
    else:
        player_game = PlayerPlayGame.objects.filter(
            game=PlayerPlayGame.objects.get(event__id=event_id).game
        )

    try:
        for p in player_game:
            player = p.player
            team = player.team.name
            if team not in result:
                result[team] = []
            result[team].append({
                'id': player.id,
                'name': player.name
            })
        return result, "Sucesso!"
    except Game.DoesNotExist:
        return None, "Jogo inexistente!"
    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter os jogadores por jogo!"


def get_info_game(id):
    result = {}

    try:
        game = Game.objects.get(id=id)

        result['id'] = id
        result['date'] = game.date
        result['journey'] = game.journey
        result['stadium'] = game.stadium.name

        game_status = GameStatus.objects.filter(game=game)

        home = game_status[0]
        away = game_status[1]

        result['home_team'] = home.team.name
        result['away_team'] = away.team.name
        result['home_goals'] = home.goals
        result['away_goals'] = away.goals
        result['home_shots'] = home.shots
        result['away_shots'] = away.shots
        result['home_ball_pos'] = home.ball_possession
        result['away_ball_pos'] = away.ball_possession
        result['home_corners'] = home.corners
        result['away_corners'] = away.corners


    except Game.DoesNotExist:
        return None, "Jogo inexistente!"

    except Exception as e:
        print(e)
        return None, "Erro na base de dados a obter a informação do jogo!"

    return result, "Sucesso"


######################### Update #########################
def update_team(data):
    transaction.set_autocommit(False)

    try:
        team = Team.objects.filter(name=data['name'])

        if not team.exists():
            return False, "Equipa a editar não existe na base de dados!"

        if data['foundation_date'] is not None:
            team.update(foundation_date=data['foundation_date'])
        if data['logo'] is not None:
            team.update(logo=data['logo'])
        if data['stadium'] is not None:
            team.update(stadium=Stadium.objects.get(name=data['stadium']))

        transaction.set_autocommit(True)
        return True, "Equipa editada com sucesso"
    except Stadium.DoesNotExist:
        return False, "Estádio inexistente!"
    except Exception as e:
        print(e)
        transaction.rollback()
        return False, "Erro na base de dados a editar as informações da equipa!"


def update_game(data):
    transaction.set_autocommit(False)

    try:
        game = Game.objects.filter(id=data['id'])

        if not game.exists():
            transaction.rollback()
            return False, "Jogo a editar nao existe na base de dados!"

        if data['date']:
            game.update(date=data['date'])
        if data['journey']:
            game.update(journey=data['journey'])
        if data['stadium']:
            game.update(stadium=Stadium.objects.get(name=data['stadium']))

        teams = game[0].teams.all()

        game_status_home = GameStatus.objects.filter(Q(game=data['id']) & Q(team=teams[0]))
        game_status_away = GameStatus.objects.filter(Q(game=data['id']) & Q(team=teams[1]))

        home_ball_pos, away_ball_pos = None, None

        if data['home_ball_pos'] is not None:
            home_ball_pos = data['home_ball_pos']
        if data['away_ball_pos'] is not None:
            away_ball_pos = data['away_ball_pos']

        if home_ball_pos is not None and away_ball_pos is not None:
            if home_ball_pos + away_ball_pos != 100:
                transaction.rollback()
                return False, "A soma das posses de bola das duas equipas deve ser igual a 100!"
            else:
                game_status_home.update(ball_possession=home_ball_pos)
                game_status_away.update(ball_possession=away_ball_pos)

        if data['home_goals']:
            game_status_home.update(goals=data['home_goals'])

        if data['away_goals']:
            game_status_away.update(goals=data['away_goals'])

        if data['home_shots']:
            game_status_home.update(shots=data['home_shots'])

        if data['away_shots']:
            game_status_away.update(shots=data['away_shots'])

        if data['home_corners']:
            game_status_home.update(corners=data['home_corners'])

        if data['away_corners']:
            game_status_away.update(corners=data['away_corners'])

        transaction.set_autocommit(True)
        return True, "Sucesso!"

    except Team.DoesNotExist:
        transaction.rollback()
        return False, "Equipa nao existente"

    except Stadium.DoesNotExist:
        transaction.rollback()
        return False, "Estadio nao existente!"

    except Game.DoesNotExist:
        transaction.rollback()
        return False, "Jogo nao existente!"

    except Exception as e:
        print(e)
        transaction.rollback()
        return False, "Erro na base de dados ao editar as informações do jogo"


def update_stadium(data):
    transaction.set_autocommit(False)

    try:
        stadium = Stadium.objects.filter(name=data['current_name'])

        if not stadium.exists():
            return False, "Estadio a editar mao existe na base de dados"

        if data['name'] is not None:
            stadium.update(name=data['name'])
            stadium = Stadium.objects.filter(name=data['name'])
        if data['number_seats'] is not None:
            stadium.update(number_seats=data['number_seats'])
        if data['picture'] is not None:
            stadium.update(picture=data['picture'])

        transaction.set_autocommit(True)
        return True, "Estadio editado com sucesso"
    except Exception as e:
        print(e)
        transaction.rollback()
        return False, "Errno na base de dados a editar as informações do estadio!"


def update_player_to_game(data):
    transaction.set_autocommit(False)

    try:
        for team in data['teams']:
            players_game = PlayerPlayGame.objects.filter(Q(game__id=data['id']) & Q(player__team__name=team))
            for p in players_game:
                p.event.all().delete()

            players_game.delete()

        add_status, message = add_player_to_game(data)

        if not add_status:
            transaction.rollback()
            return False, message

        transaction.set_autocommit(True)
        return True, "Jogadores que jogam nesse jogo editados com sucesso"
    except Game.DoesNotExist:
        transaction.rollback()
        return False, "Jogo não existente!"
    except Player.DoesNotExist:
        transaction.rollback()
        return False, "Jogador não existente!"
    except Exception as e:
        print(e)
        transaction.rollback()
        return False, "Erro na base de dados a editar jogadores que jogam nesse jogo!"


def update_player(data):
    transaction.set_autocommit(False)

    try:
        player = Player.objects.filter(id=data['id'])

        if not player.exists():
            return False, "Jogador a editar não existe na base de dados!"

        if data['name'] is not None:
            player.update(name=data['name'])
        if data['photo'] is not None:
            player.update(photo=data['photo'])
        if data['position'] is not None:
            player.update(position=Position.objects.get(name=data['position']))
        if data['birth_date'] is not None:
            player.update(birth_date=data['birth_date'])
        if data['nick'] is not None:
            player.update(nick=data['nick'])
        if data['team'] is not None:
            player.update(team=Team.objects.get(name=data['team']))

        transaction.set_autocommit(True)
        return True, "Jogador editada com sucesso"
    except Team.DoesNotExist:
        return False, "Equipa inexistente!"
    except Position.DoesNotExist:
        return False, "Posição inexistente!"
    except Exception as e:
        print(e)
        transaction.rollback()
        return False, "Erro na base de dados a editar as informações do jogador!"


def update_event(data):
    transaction.set_autocommit(False)

    try:
        event = Event.objects.filter(id=data['id'])
        player_game = PlayerPlayGame.objects.filter(event__id=data['id'])

        if not event.exists():
            transaction.rollback()
            return False, "Evento a editar não existe na base de dados!"

        if not player_game.exists():
            transaction.rollback()
            return False, "Não existe nenhum jogador atribuido ao evento a editar!"

        if data['minute'] is not None:
            event.update(minute=data['minute'])
        if data['kind_event'] is not None:
            event.update(kind_event=KindEvent.objects.get(name=data['kind_event']))
        if data['player'] is not None:
            PlayerPlayGame.objects.filter(event__id=data['id']).delete()
            PlayerPlayGame.objects.get(player__id=data['player']).event.add(Event.objects.get(id=data['id']))

        transaction.set_autocommit(True)
        return True, "Jogador editada com sucesso"
    except Event.DoesNotExist:
        transaction.rollback()
        return False, "Evento a editar não existe na base de dados!"
    except PlayerPlayGame.DoesNotExist:
        transaction.rollback()
        return False, "Jogador selecionado não jogou no referido jogo!"
    except Game.DoesNotExist:
        transaction.rollback()
        return False, "Jogo inexistente!"
    except Exception as e:
        print(e)
        transaction.rollback()
        return False, "Erro na base de dados a editar as informações do evento!"


######################### Remove #########################


def remove_team(name):
    transaction.set_autocommit(False)
    try:
        team = Team.objects.get(name=name)
        players = Player.objects.filter(team=team)

        # code to remove all game in which appears this team(this will remove player_game and their events)
        games = GameStatus.objects.filter(team=team)
        for g in games:
            remove_game_status, message = remove_game(g.game_id)
            if not remove_game_status:
                transaction.rollback()
                return False, message

        for p in players:
            remove_player_status, message = remove_player(p.id)
            if not remove_player_status:
                transaction.rollback()
                return False, message
        team.delete()
        transaction.set_autocommit(False)
        return True, "Equipa removida com sucesso"
    except Team.DoesNotExist:
        transaction.rollback()
        return False, "Equipa inexistente!"

    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro ao eliminar a equipa"


def remove_all_events_player_and_game(player_id):
    transaction.set_autocommit(False)
    try:
        player_game = PlayerPlayGame.objects.filter(player=player_id)
        for p in player_game:
            remove_status, message = remove_allplayersFrom_game(p.game)
            if not remove_status:
                transaction.rollback()
                return False, message
            remove_status, message = remove_game(p.game.id)
            if not remove_status:
                transaction.rollback()
                return False, message
        transaction.set_autocommit(True)
        return True, "Eventos do jogador removidos com sucesso"
    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro ao remover todos os eventos do jogador!"


def remove_player(id):
    transaction.set_autocommit(False)
    try:
        player = Player.objects.get(id=id)
        remove_status, message = remove_all_events_player_and_game(player.id)
        if not remove_status:
            transaction.rollback()
            return False, message

        player.delete()
        transaction.set_autocommit(True)
        return True, "Jogador removido com sucesso"

    except Player.DoesNotExist:
        transaction.rollback()
        return False, "Jogador inexistente!"
    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro ao eliminar o jogador"


def remove_stadium(name):
    transaction.set_autocommit(False)
    try:
        stadium = Stadium.objects.get(name=name)
        team = Team.objects.get(stadium=stadium)
        remove_team_status, message = remove_team(team.name)
        if not remove_team_status:
            transaction.rollback()
            return False, message

        stadium.delete()
        transaction.set_autocommit(True)
        return True, "Estadio removido com sucesso"

    except Stadium.DoesNotExist:
        transaction.rollback()
        return False, "Estadio inexistente!"

    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro ao eliminar o estadio"


def remove_allplayersFrom_game(game_id):
    try:
        for p in PlayerPlayGame.objects.filter(game=game_id):
            p.event.all().delete()
            p.delete()

        return True, "Todos os jogadores removidos com sucesso do jogo!"
    except PlayerPlayGame.DoesNotExist:
        return False, "Jogo inexistente!"

    except Exception as e:
        print(e)
        return False, "Erro ao eliminar todos os jogadores do jogo!"


def remove_game(game_id):
    transaction.set_autocommit(False)

    try:
        game = Game.objects.filter(id=game_id)
        game_status = GameStatus.objects.filter(game=game_id)

        remove_players_status, message = remove_allplayersFrom_game(game_id)  # remove player form game and their events
        if not remove_players_status:
            return False, message, None

        game_status.delete()
        game.delete()

        transaction.set_autocommit(True)
        return True, "Jogo removido com sucesso!"
    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro ao eliminar o jogo!"


def remove_event(id):
    try:
        Event.objects.filter(id=id).delete()
        return True, "Evento eliminado com sucesso!"
    except Exception as e:
        print(e)
        return False, "Erro ao eliminar o evento!"
