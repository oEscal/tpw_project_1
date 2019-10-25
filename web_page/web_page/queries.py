from django.db import transaction
from django.db.models import Max, Q

from page.models import *
from web_page.help_queries import get_players_per_team

import base64

def next_id(model):
    max_id = model.objects.aggregate(Max('id'))['id__max']
    if not max_id:
        max_id = 0

    return max_id + 1


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
            if Game.objects.filter(Q(date=data['date']) & Q(team=team_model)).exists():
                return False, f"A equipa {data['teams'][i]} já jogou no referido dia!"
            if Game.objects.filter(Q(journey=data['journey']) & Q(team=team_model)):
                return False, f"A equipa {data['teams'][i]} já jogou na referida jornada!"

            players_per_team = get_players_per_team(team_model.name)

            if len(players_per_team) < 14:
                return False, f"A equipa {data['teams'][i]} não tem jogadores suficientes inscritos (minimo 14) !"

            goal_kepper_number = len(players_per_team.filter(position=Position.objects.get(id=1)))

            if goal_kepper_number < 1:
                return False, f"A equipa {data['teams'][i]} não tem o numero pelo menos 1 guarda-redes !"
            GameStatus.objects.create(
                game=new_game,
                team=team_model,
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
        transaction.rollback()
        print(e)
        return False, "Erro na base de dados a adicionar o novo jogo!"


def add_player(data):
    # verify is player already is on that team
    if Player.objects.filter(team__name=data['team_name'], name=data['name']):
        return False, "Ja existe um jogador com este nome na equipa!"

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
            minute=data['minute']
        )

        player_play_game = PlayerPlayGame.objects.get(Q(player__id=data['player']) & Q(game__id=data['game']))
        player_play_game.event.add(new_event)

        transaction.set_autocommit(True)
        return True, "Evento adicionado com sucesso"
    except PlayerPlayGame.DoesNotExist:
        transaction.rollback()
        return False, "Este jogador não está adicionado a este jogo!"
    except Exception as e:
        transaction.rollback()
        print(e)
        return False, "Erro na base de dados a adicionar novo evento!"


def add_player_to_game(data):
    try:
        # verify if player is already on that game
        if PlayerPlayGame.objects.filter(Q(game__id=data['game']) & Q(player__id=data['player'])).exists():
            return False, "Jogador já adicionado a este jogo!"

        PlayerPlayGame.objects.create(
            game=Game.objects.get(id=data['game']),
            player=Player.objects.get(id=data['player'])
        )

        return True, "Jogador adicionado com sucesso ao jogo"
    except Game.DoesNotExist:
        return False, "Jogo não existente!"
    except Player.DoesNotExist:
        return False, "Jogador não existente!"
    except Exception as e:
        print(e)
        return False, "Erro na base de dados a adicionar novo jogador ao jogo"


######################### Get queries #########################


def get_teams():
    result = []

    default_logo = "iVBORw0KGgoAAAANSUhEUgAAAMUAAAD/CAMAAAB2B+IJAAAAkFBMVEX///8AAADi4uIMDAzHx8cvLy/m5ub8/Pz39/fu7u7z8/Px8fHq6ur29vZPT0/r6+vb29ufn5+/v799fX3T09Ozs7OYmJikpKQmJia1tbU6OjpFRUXV1dW8vLypqakrKytaWlqGhoaOjo5NTU0YGBhwcHBnZ2cgICBAQEAUFBRqampWVlYjIyM0NDR5eXlfX1/pjximAAAPpElEQVR4nO1daXuqPBDtAAriBqio4AaiuFH//797E7MA7a0liCZ9H8+X+tzrksDMmTOTSfj4eOONN95444033lARPkjEpKFJGLrMWSTjRibhzAB0aQDI2g1MYhgCnNqaLGwAzvbDk7D2ANtuA1ejJnoBwOfD3xIBrLUGRlMbiwTAf/A7VsgnjEZGUxtL5OLzh77BaJDqasNFV/IRonLQ3YwbG01tjABa9YmqizxrZzY4nJroXwEG/ZofNvGHOcs5xuvBbkDvgC5nzVkgempxehrr69aLkUEwpL++SOsS1bToVO006rVfjN74srHo7y9r0kyJnuxwL8M/DBixl/WIyrkU6Wl/eFwF1MEEXPZyVLTvisDqKfenOGlCkdWBD0v6ysJcIyaFrBI9raAZdVwHO1jQV8ODKO9HRUFsPCgAHoK1XffoSycVi8FuMTlxjo+KsYfQmw0YUXmIcFaVP+gV9VcneFwYP4RF7qBIm0JVbVrSwtb1bN178wuwzEeDLH3mVPrQEKknTtMfUat3572vgcstA+dsYRWiwvS04dJrqi/uvflF+OQk2dkCVAnAKLpk/PIbnK6loj+YMcbEtYzo1w8gejryy+/o7r33vg7t2ZZ5p1GBqDA98ctvt0b33vtKjEWICtMTv/zm5qxAikQxLxHV5R5Rlelp1Oo8c1yC8DlRmZiofh5aF9MTjw5TqMbMr8KJE1UXF/p+zGDRrQo5PXmVo+SLYIc5UWV3iMovxGwnnT59XILQdC6z/Tu6EN2pgNnbfvD8YYliANRSuoc8Jf+OSc5Qfionu7uDbsJ0qXs3ZFghMF7SZCYV/8aSeWq3BYd7EnWVT/J6ffaoRHE60PA1/SV6dwM+Sw+klsq/oweUb/oZBPd1rcsFSH8mNcX7jhUM2Qv4hT87a2DkFGVPHZQwQurb5gFav6UYPpdaY1AhteBw8nHBr0q7nTD1aAYKFP1zxC3q2yOoUB3bAYstfksdSfthrambdpIq63we9x1NJZMyGGWuKpVBrIz7d/h7avgyfLJBnSGoYiLIv+k98GfKmJTFxOmigm9jOFwvLtQxKQOoR6NrXC0abyCjKchFkeIBYqgt+YuCxb7aJybcf0abpwxJHFZGr+e48pJSR2fJtwGKZN4Os+0YjlWHdAW6dNRRJWt1W8TG+2FVg7qZFE3Uz4oUpK400FU3KJzgsvzbD54xJmF0EpqyxZBUzxc2EJJIwQlOLljgRgwlkLuhLIPUomzde8aoRMEUnSOyloTfTZltoESqtKEye1o15N1gciqIN40PSRx2Ql36xCy9GiJokfTQSyR22zE41L6H6wpLFwUsGddqKhRrJymJdAaILQppCXUMey29VQ0JoTP5G0MqVJcxt4zSrgrkGFs6hi0MxFKFCGZEhCjg3p2U2MMwEXMLvHRDHWOeyV7u5s6N3EIwerV1Gl/GuvQSoZcQs0CxWFBJWAeqzhWQtdOQ/N1BIFrH3wFZmjRbAjH/OfgkkdsO4CT6URdmJO5tpNfWzkQFaTUaID0mCEfCF6BhmBmhqLGwc+OuKLoM424ll3PshHjmCnRhHdHNaD1nOavbVdwQekfCkhGsf17L+wkDWnWWXkEYp6RuvBcTtAQnWuh0ZK8pLdeEXwUKBzliIAlW7yg5YExoXTYT1R8YKzje7qTdkqxqXVIWNNe/rYP9C0tKtWYouQmB6lE7rbN2bTA9eJYc9kaEZXrHOlrIYdXaveTK2o5U1DSok3ZqLD3c1d2/0RDoVXSE6h8MSJsTt44kNyFc2SyONXpikR0SNetvmxyTODaEYB1IxUP3Ry+hzOYe5Aopyi4OzGqIiGFKZzEN5OasAzaLdY3SWOdCizkryZn3lmQVDrRqdGx1ZjQpWbXkitqQDGMB2SOzmNS5Bg1iSyyq3iyGzKImdeyxQQzYLH7txPkHkHeTWcwvchOMhziKM+1E8iweixdHNou1XL+4slkca6zO8ergKpPLUbmOqjMLtig7rdQD8zxQTVtPDTqs/OOGTY5JHCOSbtdT5mOWX8hWgzTX06pvcivAY21S0aaxAdUCzbt7xzoZ64Tdwc8aBZQmQWsgdlqnejBlWcle8t7JJdFx5rrObvsYZkTLDiRXD4wLiXa16lE7ONz+mgfJlRyHrmYdxJcvcEcLybftluQtDB3KMgM4C3/WDGnzbS+RXOG0UzIAZBzC4beTAcuxJHcfmAHREDGshYsgWgpsCUf2puIzyRAQaQpfTx66PV12P8uOcBMvuQqAr+vJLh4gUyJh1xHsZcFYAV3CicWZoWFMiQRpCzWqEcSsG3UnOXTjxaSbNXTX4qdA7eBKeE1+z92YeKYVCp9bZA5oB4Upv0FKo8H7JNpYhCI2DRdd+X0gwwsZQixcy+npVM1LD3pYyRFzWIEumHnn4aJO5aFhbIhZGCC6H2QO1BhlV2kxPnn9QFCY+kAbJ2LJWTeGv7n96aaiedIIaBPLTnZLDsKE7K01DyC4UHqlKYm5ld4ehRyC1javIr3yH/jUJpoe2mvprWp5wIggFNJ0wxYtOPTkhwuU6xyJmJ3CTChL0I60MCi9IwfDahExa4DY2UNjpuWld0dhmANiGI5geXDJds5MWrKzCwyaJ/VSsZMTp5CRexArcVQOzZPsg5g2j4AeySY/u8BYkbK9eRXT5ntWwZKfXWB4JE/KY3ElmCxcKNDZjLE4Eknug8jqXJ+tdffV2CPWTkh6MBdaFeuxNb2exLMrC+iuCcOKFXMWrGjiyN+3gMHKg5ouos35nI1UgaCHMKC7pC7VNtoT8BzJU+QYij0lm4PIGsYU6Da9ieT1VYYRDVsbkTWMGGie6kovDBLENLH4FFnDGLHG9FjyyiSDz8bz22lFRexgQ158KiFA8r32K0irBwyWr36cFNhziLGipx14AjtJkACh92CvhIzCpElugUhJyg4YoV0VmcWSppwLgTxpOGM6/qzIsSYerbPyTLoCerx8NVDk6ESPGlL7Ul2CtFMqBqXvvWDwqCIaZtVz1nZC32selEgvsFeTWaCctfKIkPURSWsF0pdgCAzq1HZYvTEHCWDiQ1am2CysbXVRq7FmOytQxqLoLAbVZ8FbBhXyCzIL81y9+J/PYqsYRyFpLj4LlmNJB5sFuhfiFqVM7F7SWYj4RR7nVdFRc6pA+tvqTIsUCO0b2SuizCdUDaJ4UZlvOmsW53eKnOU1oU1aKHZXjmDdgN23keQdhwwsS+oE1buLrJDxWazIsccrWp/trasrc3PAsiRXkfPAp7R6oCUCq0kblrFOFDkvmNViFiKF2j3bnG8ocqr5Jz/GUeAcCr7a4RyVqDZ/XGms80QqOT6sSf2no8RjYT7MgDLTSqSqxjuRzFSJ58K0U2pHkciSmMcLJmqs6xkXul59FTlNQ+OdSNJPybmBFb3NTGSp2OalnJXkDWIE7HC39lGkpdbcsoXlsQoHcdopDdiCTdqfjAs6qQIPkDAS2oozhaPILtAV3xx3VUDV8vMjBDtqx7wz3ZXeLP/Rz6jC7rTEtiYN+fsd+W1e/JDcsWgT555vnwmlm9SOxQgfErEW5Slng2nlQ6ufhDZPKYT3Vzn8QLmeLvvMIrYzeyF8yB2KGOxZcCO57Wr8cTAfsfiu4in/iCa+BaVJRLQ3Cm9D2IgKCe3IWS2S6RkaL3p4NXb0IJZKaJwc6hKrUld+vs2AnUYpAiP3JYlP+J3zcOVVed7kN5gDYG1F5iaQtH1B01m0QsOp1as1z5/+pok22zcEa8P7szyoNwZrC7x2MKn1IPOHEfOAZ4UiJ/wXgabPM71Ihpzy8szOr/g4mH/gmu+5tM6vr4ZoKW+sdvT7z6K7ByRD+FOKu2HFxxw3hs7hwvJMc1PrGA0KdB9P7HL0guSlfGufc353a7o2AXLwPF62Q/2FvmFf86uPQlf4SKV1ocORX5Hh5nVM1TnnCxXtDPTHzACJwgOP+/0dRK8p7Ghhfifwo7gf1aO74vOyTR82r6jsGOksv/hIkD+8ojU8lPSLl8yeX7ldwSC/Vsgato+fWYAf+11IsbQzjJ57EEJnB6Nctk0Q2zex+vDlsd+WC8EzucooNXIhMXdshuAnX55evghh9KzTNewYtoXouoIaRzb8APxdxRKC5UP6HM41AvALLOhWePp7deC7ERc51tnDpnlB0vuEbcF8+qNGJ0GmsStm3+Z8DVGzZtVfHcEtZGPtTcOTQAyLmCosOXUn1pNpc2xlGlvYFckIGRfoTdstcmnQ/VLkdkZwmDcUy40rbItdBRaKdc/gwt4efe+17AyLE5yNBuaBvieYFPWec0Y/dnqGTLB8HSB1S3UE0xjA/lE+R/d0Ni3Ooe8maBL+k0qSBrIqdPFL/2bOD/D5SBqoRZD4pbLdGN+I4HkbBYcR+n49KpcK7dUFRnVFQic+Qtz++i+I1596aJWBxCFkk/LN7qCcMK5x7OpHF5nOZ+kCmPMM/cD22elYP06+m9VHewTpVDQds1dr2JXpYoxyCUif5RHffunrz38sdohmROjKnARwKhODM0L8AfvXFFusJTar5KvpGmcYVKZdywthU353O0rR14bLl62W2P4a/eDaLfsCpquKF9LYwMArzaHn4q9suS/tx9JGmEkOq/KP9qcz8H8fB/KioBz07Sm+vcfo5Y0O4x12j+0XumpHX+TWd1irFMoBwppsb64mY33BHGNNgiyjPA/ExXdzqAWK9iVmwPEff08TUqYWjBtdXcsXv+/D5cfF9U4EWfk/DXItmpKVdWAub9fxC2MuNnD691LgvAVxSc0Tuwwnkg+p6s+D7+HDXOmzf3hHZwfn0vucHQ4QZTkrCbbbuqmrkpJAiZr71UaMVimpxjoQz0E45j8JvRhlgnApEY/pw77s5G4pqUYaCn8oc9U4kuAGJ7qFjxLtGq11YdT2DqLCRTfn4W3iCnTCFUFM/Fy82siqeC1JC0v1dgcT07G2nn8ibrSrF0O3NWI1jPFsXZAmfRcrpqsSR418gzXJvt6OmNwBQ98WTIfkchPpPXA/oRchs0qKROTjtV4DznmQMG9JdcO1rIYxxlHwVBjiCIwxDHIi0k6YBqR38f2CW6Uky0dpXkEP80kssf6OFGLXn4D0B+j5EnsnOPBbY+JaWab6jSC41fU+uSdonE+H2Jr2SntEER4iq8G3YODgIuk3XaIwNBTVsi/xwFj/GWtiQAEPklIiMUFef1YwWN8HXgcqtNFMsa8ool5FMNcLi7M+Lh//IZfIscyn4X9ZGfxL8IBOA5uTAvs4asIjt2DypydBx4+X/RU5kaMmkEPox7/rEwx4zVpSH2uDsJA2HPzBOPEFvUD8cfQKwvjrTvHGG2+88cYbb7zxP8Z/Vf3jtBKM6VUAAAAASUVORK5CYII="


    try:
        for t in Team.objects.all():
            print(t.logo)
            result.append({
                'name': t.name,
                'logo': t.logo if t.logo is not None else default_logo,
                'foundation_date': t.foundation_date,
                'stadium_name': t.stadium.name
            })
    except Exception as e:

        return None, "Erro na base de dados a obter todas as equipas!"

    return result, "Sucesso"
