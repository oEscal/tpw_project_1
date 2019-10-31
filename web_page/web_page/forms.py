from django import forms

from web_page.help_queries import *


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
                                 help_text="Insira a data de nascimento do jogador", required=False, widget=DateInput())
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


class Game(forms.Form):
    date = forms.DateField(label="Data do jogo", help_text="Insira a data do jogo", required=True, widget=DateInput())
    journey = forms.IntegerField(label="Jornada do Jogo", help_text="Insira a jornada do jogo", required=True)
    stadium = forms.ChoiceField(label="Estádio do jogo", help_text="Insira o estádio do jogo", required=True)

    home_team = forms.ChoiceField(label="Equipa local", help_text="Insira a equipa local", required=True)
    away_team = forms.ChoiceField(label="Equipa visitante", help_text="Insira a equipa visitante", required=True)

    home_shots = forms.IntegerField(label="Remates da equipa local", help_text="Insira os remates da equipa local",
                                    required=True)
    away_shots = forms.IntegerField(label="Remates da equipa visitante",
                                    help_text="Insira os remates da equipa visitanten", required=True)
    home_ball_pos = forms.IntegerField(label="Posse de bola da equipa local",
                                       help_text="Insira a posse de bola da equipa local", required=True)
    away_ball_pos = forms.IntegerField(label="Posse de bola da equipa visitante",
                                       help_text="Insira a posse de bola da equipa visitante", required=True)
    home_corners = forms.IntegerField(label="Cantos da equipa local", help_text="Insira os cantos da equipa local",
                                      required=True)
    away_corners = forms.IntegerField(label="Cantos da equipa visitante",
                                      help_text="Insira os cantos da equipa visitante", required=True)

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
            data = game["data"]
            for field_name, field in self.fields.items():
                field.initial = data[field_name]
