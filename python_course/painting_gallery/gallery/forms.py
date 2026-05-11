from django import forms
from .models import Painting, Artist, Style


class PaintingForm(forms.ModelForm):
    class Meta:
        model = Painting
        fields = ['title', 'artist', 'style', 'year', 'technique',
                  'width_cm', 'height_cm', 'museum', 'description', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название картины'}),
            'artist': forms.Select(attrs={'class': 'form-select'}),
            'style': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 1889'}),
            'technique': forms.Select(attrs={'class': 'form-select'}),
            'width_cm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ширина в см'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Высота в см'}),
            'museum': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Музей Орсе, Париж'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                  'placeholder': 'Описание картины...'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control',
                                               'placeholder': 'https://...'}),
        }
        labels = {
            'title': 'Название',
            'artist': 'Художник',
            'style': 'Стиль',
            'year': 'Год создания',
            'technique': 'Техника',
            'width_cm': 'Ширина (см)',
            'height_cm': 'Высота (см)',
            'museum': 'Музей / Место хранения',
            'description': 'Описание',
            'image_url': 'Ссылка на изображение',
        }


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['first_name', 'last_name', 'birth_year', 'death_year',
                  'nationality', 'biography', 'style']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год рождения'}),
            'death_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год смерти'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Французский'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'style': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'birth_year': 'Год рождения',
            'death_year': 'Год смерти',
            'nationality': 'Национальность',
            'biography': 'Биография',
            'style': 'Основной стиль',
        }


class StyleForm(forms.ModelForm):
    class Meta:
        model = Style
        fields = ['name', 'description', 'period']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Импрессионизм'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XIX век'}),
        }
        labels = {
            'name': 'Название стиля',
            'description': 'Описание',
            'period': 'Исторический период',
        }
