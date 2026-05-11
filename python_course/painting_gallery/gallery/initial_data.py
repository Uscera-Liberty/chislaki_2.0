"""
Запустите этот скрипт через:
    python manage.py shell < gallery/initial_data.py
или вручную внутри shell.
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'painting_gallery.settings')
django.setup()

from gallery.models import Style, Artist, Painting

# Стили
impressionism = Style.objects.get_or_create(
    name='Импрессионизм',
    defaults={'period': 'XIX век', 'description': 'Направление, возникшее во Франции в 1860-х годах. Основная цель — передать мимолётные впечатления и изменчивость света.'}
)[0]
realism = Style.objects.get_or_create(
    name='Реализм',
    defaults={'period': 'XIX век', 'description': 'Направление, стремящееся к точному и объективному изображению действительности.'}
)[0]
renaissance = Style.objects.get_or_create(
    name='Возрождение',
    defaults={'period': 'XIV–XVII вв.', 'description': 'Эпоха расцвета искусства, ориентированного на античные идеалы.'}
)[0]
post_impressionism = Style.objects.get_or_create(
    name='Постимпрессионизм',
    defaults={'period': 'Конец XIX – начало XX в.', 'description': 'Продолжение импрессионизма с усилением выразительности и личного начала.'}
)[0]
baroque = Style.objects.get_or_create(
    name='Барокко',
    defaults={'period': 'XVII–XVIII вв.', 'description': 'Стиль, отличающийся динамизмом, роскошью и сложностью форм.'}
)[0]

# Художники
monet = Artist.objects.get_or_create(
    first_name='Клод', last_name='Моне',
    defaults={'birth_year': 1840, 'death_year': 1926, 'nationality': 'Французский',
              'style': impressionism,
              'biography': 'Основоположник импрессионизма. Прославился серией картин «Водяные лилии», «Стога сена» и видами Руанского собора. Работал на открытом воздухе, стараясь запечатлеть мгновение.'}
)[0]
vangogh = Artist.objects.get_or_create(
    first_name='Винсент', last_name='Ван Гог',
    defaults={'birth_year': 1853, 'death_year': 1890, 'nationality': 'Нидерландский',
              'style': post_impressionism,
              'biography': 'Один из величайших художников постимпрессионизма. За свою жизнь создал более 2000 работ. Экспрессивная манера письма оказала огромное влияние на искусство XX века.'}
)[0]
leonardo = Artist.objects.get_or_create(
    first_name='Леонардо', last_name='да Винчи',
    defaults={'birth_year': 1452, 'death_year': 1519, 'nationality': 'Итальянский',
              'style': renaissance,
              'biography': 'Универсальный гений эпохи Возрождения. Живописец, скульптор, архитектор, учёный и изобретатель. Автор «Моны Лизы» и «Тайной вечери».'}
)[0]
rembrandt = Artist.objects.get_or_create(
    first_name='Рембрандт', last_name='ван Рейн',
    defaults={'birth_year': 1606, 'death_year': 1669, 'nationality': 'Нидерландский',
              'style': baroque,
              'biography': 'Величайший мастер нидерландской живописи XVII века. Прославился своими портретами, автопортретами и библейскими сценами.'}
)[0]
repin = Artist.objects.get_or_create(
    first_name='Илья', last_name='Репин',
    defaults={'birth_year': 1844, 'death_year': 1930, 'nationality': 'Русский',
              'style': realism,
              'biography': 'Крупнейший русский живописец-реалист. Автор монументальных полотен «Бурлаки на Волге», «Запорожцы», «Иван Грозный и сын его Иван».'}
)[0]

# Картины
paintings_data = [
    {'title': 'Впечатление. Восход солнца', 'artist': monet, 'style': impressionism,
     'year': 1872, 'technique': 'oil', 'height_cm': 48, 'width_cm': 63,
     'museum': 'Музей Мармоттан Моне, Париж',
     'description': 'Картина, давшая название целому направлению в живописи — импрессионизму. Изображает гавань Гавра на рассвете.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Monet_-_Impression%2C_Sunrise.jpg/1280px-Monet_-_Impression%2C_Sunrise.jpg'},
    {'title': 'Водяные лилии', 'artist': monet, 'style': impressionism,
     'year': 1906, 'technique': 'oil', 'height_cm': 89, 'width_cm': 92,
     'museum': 'Чикагский институт искусств',
     'description': 'Одна из серии картин, изображающих пруд с нимфеями в саду художника в Живерни.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg/1280px-Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg'},
    {'title': 'Звёздная ночь', 'artist': vangogh, 'style': post_impressionism,
     'year': 1889, 'technique': 'oil', 'height_cm': 73.7, 'width_cm': 92.1,
     'museum': 'Музей современного искусства, Нью-Йорк',
     'description': 'Ночной пейзаж, написанный в больнице Сен-Поль-де-Мозоль. Одно из самых узнаваемых произведений западной живописи.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg'},
    {'title': 'Подсолнухи', 'artist': vangogh, 'style': post_impressionism,
     'year': 1888, 'technique': 'oil', 'height_cm': 92.1, 'width_cm': 73,
     'museum': 'Национальная галерея, Лондон',
     'description': 'Серия натюрмортов с подсолнухами. Ван Гог использовал различные оттенки жёлтого без применения других цветов.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Vincent_van_Gogh_-_Sunflowers_-_VGM_F458.jpg/800px-Vincent_van_Gogh_-_Sunflowers_-_VGM_F458.jpg'},
    {'title': 'Мона Лиза', 'artist': leonardo, 'style': renaissance,
     'year': 1517, 'technique': 'oil', 'height_cm': 77, 'width_cm': 53,
     'museum': 'Лувр, Париж',
     'description': 'Самый известный портрет в истории живописи. Изображает Лизу Герардини, жену флорентийского торговца Франческо дель Джокондо.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg'},
    {'title': 'Ночной дозор', 'artist': rembrandt, 'style': baroque,
     'year': 1642, 'technique': 'oil', 'height_cm': 363, 'width_cm': 437,
     'museum': 'Рейксмюсеум, Амстердам',
     'description': 'Групповой портрет стрелковой роты под командованием Франса Баннинга Кока. Шедевр золотого века нидерландской живописи.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Night_Watch_-_HD.jpg/1280px-The_Night_Watch_-_HD.jpg'},
    {'title': 'Бурлаки на Волге', 'artist': repin, 'style': realism,
     'year': 1873, 'technique': 'oil', 'height_cm': 131.5, 'width_cm': 281,
     'museum': 'Русский музей, Санкт-Петербург',
     'description': 'Монументальная картина, изображающая тяжёлый труд бурлаков. Стала символом русского реализма и социальной живописи XIX века.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Repin_Barge_Haulers.jpg/1280px-Repin_Barge_Haulers.jpg'},
    {'title': 'Запорожцы пишут письмо турецкому султану', 'artist': repin, 'style': realism,
     'year': 1891, 'technique': 'oil', 'height_cm': 203, 'width_cm': 358,
     'museum': 'Русский музей, Санкт-Петербург',
     'description': 'Репин работал над этой картиной 11 лет. Изображает запорожских казаков, сочиняющих ответ турецкому султану.',
     'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Ilja_Jefimowitsch_Repin_-_Reply_of_the_Zaporozhian_Cossacks_-_Yorck.jpg/1280px-Ilja_Jefimowitsch_Repin_-_Reply_of_the_Zaporozhian_Cossacks_-_Yorck.jpg'},
]

for data in paintings_data:
    Painting.objects.get_or_create(
        title=data['title'],
        artist=data['artist'],
        defaults={k: v for k, v in data.items() if k not in ('title', 'artist')}
    )

print("✅ Начальные данные успешно загружены!")
print(f"   Стилей: {Style.objects.count()}")
print(f"   Художников: {Artist.objects.count()}")
print(f"   Картин: {Painting.objects.count()}")
