from django.db import models


class Style(models.Model):
    """Художественный стиль (импрессионизм, реализм и т.д.)"""
    name = models.CharField('Название стиля', max_length=100, unique=True)
    description = models.TextField('Описание стиля', blank=True)
    period = models.CharField('Исторический период', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Стиль'
        verbose_name_plural = 'Стили'
        ordering = ['name']

    def __str__(self):
        return self.name


class Artist(models.Model):
    """Художник"""
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    birth_year = models.IntegerField('Год рождения', null=True, blank=True)
    death_year = models.IntegerField('Год смерти', null=True, blank=True)
    nationality = models.CharField('Национальность', max_length=100, blank=True)
    biography = models.TextField('Биография', blank=True)
    style = models.ForeignKey(
        Style,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Основной стиль',
        related_name='artists'
    )

    class Meta:
        verbose_name = 'Художник'
        verbose_name_plural = 'Художники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def life_years(self):
        if self.birth_year and self.death_year:
            return f'{self.birth_year}–{self.death_year}'
        elif self.birth_year:
            return f'р. {self.birth_year}'
        return '—'


class Painting(models.Model):
    """Картина — главная модель"""
    TECHNIQUE_CHOICES = [
        ('oil', 'Масло'),
        ('watercolor', 'Акварель'),
        ('tempera', 'Темпера'),
        ('fresco', 'Фреска'),
        ('pastel', 'Пастель'),
        ('acrylic', 'Акрил'),
        ('gouache', 'Гуашь'),
        ('other', 'Другое'),
    ]

    title = models.CharField('Название', max_length=200)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        verbose_name='Художник',
        related_name='paintings'
    )
    style = models.ForeignKey(
        Style,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Стиль',
        related_name='paintings'
    )
    year = models.IntegerField('Год создания', null=True, blank=True)
    technique = models.CharField('Техника', max_length=20, choices=TECHNIQUE_CHOICES, default='oil')
    width_cm = models.DecimalField('Ширина (см)', max_digits=7, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField('Высота (см)', max_digits=7, decimal_places=1, null=True, blank=True)
    museum = models.CharField('Музей / Место хранения', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    image_url = models.URLField('Ссылка на изображение', blank=True,
                                help_text='Вставьте прямую ссылку на изображение картины')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Картина'
        verbose_name_plural = 'Картины'
        ordering = ['-year', 'title']

    def __str__(self):
        return f'{self.title} ({self.artist})'

    @property
    def dimensions(self):
        if self.width_cm and self.height_cm:
            return f'{self.height_cm} × {self.width_cm} см'
        return '—'
