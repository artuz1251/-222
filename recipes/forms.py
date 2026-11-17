import re
from django import forms
from django.core.exceptions import ValidationError


def no_control_chars(value):
    # Управляющие символы ломают XML, поэтому запрещаем их
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', value):
        raise ValidationError('Недопустимые символы в тексте')


class RecipeForm(forms.Form):
    name = forms.CharField(label='Название', max_length=100, validators=[no_control_chars])
    category = forms.CharField(label='Категория', max_length=50, validators=[no_control_chars])
    cook_time = forms.IntegerField(label='Время приготовления (мин)', min_value=1, max_value=1440)
    servings = forms.IntegerField(label='Количество порций', min_value=1, max_value=100)
    ingredients = forms.CharField(label='Ингредиенты', max_length=1000,
                                  widget=forms.Textarea(attrs={'rows': 4}),
                                  validators=[no_control_chars])
    instructions = forms.CharField(label='Способ приготовления', max_length=3000,
                                   widget=forms.Textarea(attrs={'rows': 6}),
                                   validators=[no_control_chars])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'


class RecipeAddForm(RecipeForm):
    """Форма добавления: пользователь выбирает, куда сохранять."""
    storage = forms.ChoiceField(label='Куда сохранить',
                                choices=[('db', 'В базу данных (SQLite)'), ('xml', 'В XML-файл')])


class UploadForm(forms.Form):
    file = forms.FileField(label='XML-файл', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.xml'):
            raise ValidationError('Разрешены только файлы .xml')
        if f.size > 1024 * 1024:
            raise ValidationError('Файл слишком большой (максимум 1 МБ)')
        return f
