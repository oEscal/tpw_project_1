from django import forms


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

        for field_name, field in self.fields.items():
            if field_name != 'picture':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.help_text

        # for the update form
        if stadium:
            data = stadium["data"]
            for field_name, field in self.fields.items():
                field.initial = data[field_name]
