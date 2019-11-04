from django import forms

from web_page.help_queries import *
from web_page.settings import MAX_PLAYERS_MATCH


class DateInput(forms.DateInput):
    input_type = 'date'


class Stadium(forms.Form):
    name = forms.CharField(label="Nome do estádio", required=True, max_length=200,
                           help_text="Insira o nome do estádio")
    address = forms.CharField(label="Endereço do estádio", required=True, max_length=200,
                              help_text="Insira o endereço do estádio")
    number_seats = forms.IntegerField(label="Número de cadeiras", required=True, min_value=0,
                                      help_text="Insira o número de cadeiras")
    picture = forms.ImageField(label="Fotografia", required=False)

    def __init__(self, stadium=None, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        # change inputs attrs
        for field_name, field in self.fields.items():
            if field_name != 'picture':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.help_text

        # for the update form
        if stadium:
            self.fields['address'].widget.attrs['readonly'] = "readonly"
            self.fields['address'].required = False
            for field_name, field in self.fields.items():
                if field_name != 'picture':
                    field.initial = stadium[field_name]


class Team(forms.Form):
    name = forms.CharField(label="Nome da equipa", help_text="Insira o nome da equipa", required=True, max_length=200)
    foundation_date = forms.DateField(label="Data de fundação", help_text="Insira a data de fundação  da equipa",
                                      widget=DateInput(), required=False)
    logo = forms.ImageField(label="Logótipo da equipa", help_text="Insira o logótipo da equipa ", required=False)

    stadium = forms.ChoiceField(label="Estádio da equipa", help_text="Insira o nome do estádio da equipa",
                                required=True)

    def __init__(self, team=None, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        # for showing all current stadiums in the stadium input
        stadium_field = self.fields['stadium']
        stadium_choices = [("-", stadium_field.help_text)]
        all_stadiums = get_all_stadium_for_team(team['stadium'] if team else None)

        for stadium in all_stadiums:
            stadium_choices.append((stadium.name, stadium.name))
        stadium_field.choices = stadium_choices

        # change inputs attrs
        for field_name, field in self.fields.items():
            if field_name != 'logo':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.help_text

        # for the update form
        if team:
            self.fields['name'].widget.attrs['readonly'] = "readonly"
            self.fields['name'].required = False
            for field_name, field in self.fields.items():
                if field_name != 'logo':
                    field.initial = team[field_name]


class Player(forms.Form):
    name = forms.CharField(label="Nome do jogador", help_text="Insira o nome do jogador", required=True, max_length=200)
    birth_date = forms.DateField(label="Data de nascimento do jogador",
                                 help_text="Insira a data de nascimento do jogador", required=False, widget=DateInput())
    photo = forms.ImageField(label="Foto do jogador", help_text="Insira a foto do jogador", required=False)
    nick = forms.CharField(label="Alcunha do jogador", help_text="Insira a alcunha do jogador", required=False,
                           max_length=200)
    position = forms.ChoiceField(label="Posição do Jogador", help_text="Insira a posição do jogador",
                                 required=True)
    team = forms.ChoiceField(label="Equipa do Jogador", help_text="Insira a equipa do jogador", required=True)

    def __init__(self, player=None, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        position_field = self.fields['position']
        team_field = self.fields['team']

        all_positions = get_all_positions()
        all_teams = get_all_teams()
        position_choices = [("-", position_field.help_text)]
        team_choices = [("-", team_field.help_text)]

        for position in all_positions:
            position_choices.append((position.name, position.name))

        for team in all_teams:
            team_choices.append((team.name, team.name))

        position_field.choices = position_choices
        team_field.choices = team_choices

        for field_name, field in self.fields.items():
            if field_name != 'photo':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.help_text

        if player:
            for field_name, field in self.fields.items():
                if field_name != "photo":
                    field.initial = player[field_name]


class PlayersToGame(forms.Form):
    def __init__(self, players=None, game_id=None, *args, **kwargs):
        super(PlayersToGame, self).__init__(*args, **kwargs)

        current_players = get_game_team_players(game_id)
        self.teams = []

        for n in range(MAX_PLAYERS_MATCH):
            for team in current_players:
                if team not in self.teams:
                    self.teams.append(team)
                self.fields[f"{team}-{n}"] = \
                    forms.ChoiceField(label=f"Jogador {n + 1}", help_text="Escolha um jogador", required=True)

                player_field = self.fields[f"{team}-{n}"]
                player_field.widget.attrs['class'] = 'form-control'

                choices = [("-", player_field.help_text)]
                for player in current_players[team]:
                    choices.append((player['id'], player['name']))
                player_field.choices = choices

                if players:
                    if len(players[team]) > 0:
                        player_field.initial = players[team][0]['id']
                        players[team].remove(players[team][0])


class Game(forms.Form):
    date = forms.DateField(label="Data do jogo", help_text="Insira a data do jogo",
                           required=True, widget=DateInput())
    journey = forms.IntegerField(label="Jornada do Jogo", help_text="Insira a jornada do jogo",
                                 min_value=0, required=True)
    stadium = forms.ChoiceField(label="Estádio do jogo", help_text="Insira o estádio do jogo", required=True)

    home_team = forms.ChoiceField(label="Equipa local", help_text="Insira a equipa local", required=True)
    away_team = forms.ChoiceField(label="Equipa visitante", help_text="Insira a equipa visitante", required=True)

    home_goals = forms.IntegerField(label="Golos da equipa local", help_text="Insira os golos da equipa local",
                                    min_value=0, required=True)
    away_goals = forms.IntegerField(label="Golos da equipa visitante", help_text="Insira os golos da equipa visitante",
                                    min_value=0, required=True)
    home_shots = forms.IntegerField(label="Remates da equipa local", help_text="Insira os remates da equipa local",
                                    min_value=0, required=True)
    away_shots = forms.IntegerField(label="Remates da equipa visitante",
                                    help_text="Insira os remates da equipa visitante", min_value=0, required=True)
    home_ball_pos = forms.IntegerField(label="Posse de bola da equipa local",
                                       help_text="Insira a posse de bola da equipa local", min_value=0, required=True)
    away_ball_pos = forms.IntegerField(label="Posse de bola da equipa visitante",
                                       help_text="Insira a posse de bola da equipa visitante", min_value=0,
                                       required=True)
    home_corners = forms.IntegerField(label="Cantos da equipa local", help_text="Insira os cantos da equipa local",
                                      min_value=0, required=True)
    away_corners = forms.IntegerField(label="Cantos da equipa visitante",
                                      help_text="Insira os cantos da equipa visitante", min_value=0, required=True)

    def __init__(self, game=None, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        stadium_field = self.fields['stadium']
        home_team_field = self.fields['home_team']
        away_team_field = self.fields['away_team']

        all_stadiums = get_all_stadium()
        all_teams = get_all_teams()

        stadiums_choices = [("-", stadium_field.help_text)]
        home_team_choices = [("-", home_team_field.help_text)]

        for stadium in all_stadiums:
            stadiums_choices.append((stadium.name, stadium.name))

        for team in all_teams:
            home_team_choices.append((team.name, team.name))

        stadium_field.choices = stadiums_choices
        home_team_field.choices = home_team_choices
        away_team_field.choices = [("-", away_team_field.help_text)] + home_team_choices[1:]

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.help_text

        if game:
            for field_name, field in self.fields.items():
                field.initial = game[field_name]
            self.fields['home_team'].choices = [(game['home_team'], game['home_team'])]
            self.fields['home_team'].required = False
            self.fields['away_team'].choices = [(game['away_team'], game['away_team'])]
            self.fields['away_team'].required = False


class Event(forms.Form):
    team = forms.ChoiceField(label="Equipa", help_text="Escolha a equipa", required=True)
    player1 = forms.ChoiceField(label="Jogador", help_text="Escolha o jogador", required=True)
    player2 = forms.ChoiceField(label="Jogador", help_text="Escolha o jogador", required=True)
    kind_event = forms.ChoiceField(label="Tipo de evento", help_text="Escolha o tipo de evento", required=True)
    minute = forms.IntegerField(label="Minuto do evento", help_text="Escolha o minuto do evento",
                                min_value=0, required=True)

    def __init__(self, event=None, game_id=None, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        # fill form
        if event:
            fill_form = get_info_for_add_event(event_id=event['id'])
        else:
            fill_form = get_info_for_add_event(game_id=game_id)

        teams_field = self.fields['team']
        players1_field = self.fields['player1']
        players2_field = self.fields['player2']
        events_field = self.fields['kind_event']

        teams_field.choices = [("-", teams_field.help_text)]
        players1_field.choices = [("-", players1_field.help_text)]
        players2_field.choices = [("-", players2_field.help_text)]
        events_field.choices = [("-", events_field.help_text)]

        count = 0
        for team in fill_form['teams']:
            teams_field.choices.append((team, team))
            for player in fill_form['teams'][team]:
                if count == 0:
                    players1_field.widget.attrs['class'] = f"form-control {team}"
                    players1_field.choices.append((player['id'], player['name']))
                else:
                    players2_field.widget.attrs['class'] = f"form-control {team}"
                    players2_field.choices.append((player['id'], player['name']))
            count += 1
        players1_field.widget.attrs['style'] = f"display: none;"
        players2_field.widget.attrs['style'] = f"display: none;"

        for kind_event in fill_form['events']:
            events_field.choices.append((kind_event, kind_event))

        for field_name, field in self.fields.items():
            if field_name != 'player1' and field_name != 'player2':
                field.widget.attrs['class'] = 'form-control'

            field.widget.attrs['placeholder'] = field.help_text

        if event:
            for field_name, field in self.fields.items():
                if field_name == 'player1' or field_name == 'player2':
                    field.initial = event['player']
                else:
                    field.initial = event[field_name]
