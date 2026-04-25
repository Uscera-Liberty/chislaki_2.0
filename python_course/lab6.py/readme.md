## Функционал

### ✅ Задание 1: БД SQLite3
- ✅ 3 связанных таблицы (artists, paintings, exhibitions)
- ✅ Автоматическое заполнение данными при старте
- ✅ 4 статистических SELECT-запроса:
  - `/stats/paintings-by-artist` - количество картин по художникам
  - `/stats/paintings-by-style` - количество картин по стилям
  - `/stats/exhibitions-by-location` - выставки по локациям
  - `/stats/artist-exhibitions` - художники и их выставки

### ✅ Задание 2: FastAPI
- ✅ Инициализация FastAPI
- ✅ Подключение к SQLite БД
- ✅ Endpoints для получения данных:
  - `GET /artists` - все художники
  - `GET /paintings` - все картины
  - `GET /exhibitions` - все выставки
- ✅ Endpoints для добавления записей:
  - `POST /artists` - добавить художника
  - `POST /paintings` - добавить картину
  - `POST /exhibitions` - добавить выставку
- ✅ HTML формы с Jinja2 шаблонами:
  - `/artists/form` - форма добавления художника
  - `/paintings/form` - форма добавления картины
  - `/exhibitions/form` - форма добавления выставки
- ✅ Вывод таблиц: `/tables` - все таблицы в HTML

### ✅ Задание 3: Экспорт/Импорт JSON
- ✅ `GET /export/artists/json` - экспорт artists в JSON
- ✅ `GET /export/paintings/json` - экспорт paintings в JSON
- ✅ `POST /import/artists/json` - импорт artists из JSON
- ✅ Сохранение в файлы: `artists_export.json`, `paintings_export.json`
- ✅ Импорт из файла: `artists_import.json`

## API Endpoints

### Просмотр данных
- `GET /` - главная страница
- `GET /tables` - все таблицы в HTML
- `GET /artists` - список художников (JSON)
- `GET /paintings` - список картин (JSON)
- `GET /exhibitions` - список выставок (JSON)

### Формы добавления
- `GET /artists/form` - форма добавления художника
- `GET /paintings/form` - форма добавления картины
- `GET /exhibitions/form` - форма добавления выставки

### Добавление данных
- `POST /artists` - добавить художника
- `POST /paintings` - добавить картину
- `POST /exhibitions` - добавить выставку

### Статистика
- `GET /stats/paintings-by-artist`
- `GET /stats/paintings-by-style`
- `GET /stats/exhibitions-by-location`
- `GET /stats/artist-exhibitions`

### Экспорт/Импорт
- `GET /export/artists/json`
- `GET /export/paintings/json`
- `POST /import/artists/json`