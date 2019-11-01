from django import forms

from web_page.help_queries import *
from web_page.settings import MIN_PLAYERS_MATCH, MAX_PLAYERS_MATCH


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
            data = stadium["data"]
            for field_name, field in self.fields.items():
                field.initial = data[field_name]


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
        all_stadiums = get_all_stadium_for_team()

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
            data = team["data"]
            for field_name, field in self.fields.items():
                field.initial = data[field_name]


class Player(forms.Form):
    name = forms.CharField(label="Nome do jogador", help_text="Insira o nome do jogador", required=True, max_length=200)
    birth_date = forms.DateField(label="Data de nascimento do jogador",
                                 help_text="Insira a data de nascimento do jogador", widget=DateInput(), required=False)
    photo = forms.ImageField(label="Foto do jogador", help_text="Insira a foto do jogador", required=False)
    nick = forms.CharField(label="Alcunha do jogador", help_text="Insira a alcunha do jogador", required=False,
                           max_length=200)
    position_name = forms.ChoiceField(label="Posição do Jogador", help_text="Insira a posição do jogador",
                                      required=True)
    team_name = forms.CharField(label="Equipa do Jogador", help_text="Insira a equipa do jogador", required=True,
                                max_length=200)

    def __init__(self, player=None, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        position_field = self.fields['position_name']

        all_positions = get_all_positions()
        position_choices = [("-", position_field.help_text)]

        for position in all_positions:
            position_choices.append((position.name, position.name))

        position_field.choices = position_choices

        for field_name, field in self.fields.items():
            if field_name != 'photo':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.help_text

        if player:
            data = player["data"]
            for field_name, field in self.fields.items():
                field.initial = data[field_name]


class PlayersToGame(forms.Form):
    def __init__(self, game_id=None, *args, **kwargs):
        players = get_game_team_players(game_id)
        self.teams = []

        super(PlayersToGame, self).__init__(*args, **kwargs)
        for t in players:
            self.teams.append(t)
            for n in range(MAX_PLAYERS_MATCH):
                self.fields[f"{t}-{n}"] = \
                    forms.ChoiceField(label=f"Jogador {n + 1}", help_text="Escolha um jogador", required=True)

                player_field = self.fields[f"{t}-{n}"]
                player_field.widget.attrs['class'] = 'form-control'

                choices = [("-", player_field.help_text)]
                for player in players[t]:
                    choices.append((player['id'], player['name']))
                player_field.choices = choices
