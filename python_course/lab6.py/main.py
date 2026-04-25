from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import json
import os
from typing import Optional

app = FastAPI()

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация БД
def init_db():
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    
    # Таблица художников
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_year INTEGER,
            country TEXT,
            image TEXT DEFAULT 'default_artist.jpg'
        )
    ''')
    
    # Таблица картин
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paintings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist_id INTEGER,
            year INTEGER,
            style TEXT,
            image TEXT DEFAULT 'default_painting.jpg',
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        )
    ''')
    
    # Таблица выставок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exhibitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            painting_id INTEGER,
            start_date TEXT,
            location TEXT,
            image TEXT DEFAULT 'default_exhibition.jpg',
            FOREIGN KEY (painting_id) REFERENCES paintings(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Заполнение БД данными
def populate_db():
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM artists')
    if cursor.fetchone()[0] == 0:
        artists = [
            ('Victoria', 2000, 'Russia', 'Victoria.jpeg'),
            ('Егор', 2001, 'Russia', 'Егор.jpeg'),
            ('Илюша', 2002, 'Russia', 'Илюша.jpeg'),
            ('Анапа вайб мастер', 1999, 'Russia', 'Анапа 2007 евангелион.jpeg'),
            ('МУСЯ художник', 2020, 'Catland', 'МУСЯ ТЫ ЧЕ.jpeg')
        ]
        cursor.executemany('INSERT INTO artists (name, birth_year, country, image) VALUES (?, ?, ?, ?)', artists)
        
        paintings = [
            ('Анапа вайб', 5, 2023, 'Vibe', 'Анапа 2007 евангелион.jpeg'),
            ('МУСЯ арт', 5, 2023, 'Cat-art', 'МУСЯ ТЫ ЧЕ.jpeg'),
            ('Евангелион момент', 5, 2023, 'Anime', '#евангелион.jpeg'),
            ('Поездка', 5, 2023, 'Travel', 'Еду с Анапы.jpeg'),
            ('Летний вайб', 5, 2023, 'Vibe', 'ну ета тупа вайб анапа 2007.jpeg'),
            ('Цветочный вайб', 5, 2023, 'Vibe', 'Плюс вайб🌼.jpeg'),
            ('Котята', 5, 2023, 'Cute', 'картинки с котятами.jpeg')
        ]
        cursor.executemany('INSERT INTO paintings (title, artist_id, year, style, image) VALUES (?, ?, ?, ?, ?)', paintings)
        
        exhibitions = [
            ('Анапа экспо', 4, '2025-01-10', 'Anapa', 'Анапа 2007 евангелион.jpeg'),
            ('Евангелион шоу', 2, '2025-02-15', 'Tokyo', '#евангелион.jpeg'),
            ('Котики арт', 4, '2025-03-01', 'Cat City', 'картинки с котятами.jpeg'),
            ('МУСЯ галерея', 5, '2025-04-01', 'Catland', 'МУСЯ ТЫ ЧЕ.jpeg'),
            ('Вайб выставка', 1, '2025-05-01', 'Sochi', 'Плюс вайб🌼.jpeg')
        ]
        cursor.executemany('INSERT INTO exhibitions (name, painting_id, start_date, location, image) VALUES (?, ?, ?, ?, ?)', exhibitions)
    
    conn.commit()
    conn.close()

init_db()
populate_db()

# === ГЛАВНАЯ СТРАНИЦА ===
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# === ПРОСМОТР ТАБЛИЦ ===
@app.get("/tables", response_class=HTMLResponse)
async def view_tables(request: Request):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM artists')
    artists = cursor.fetchall()
    
    cursor.execute('''
        SELECT p.id, p.title, a.name, p.year, p.style, p.image
        FROM paintings p
        LEFT JOIN artists a ON p.artist_id = a.id
    ''')
    paintings = cursor.fetchall()
    
    cursor.execute('''
        SELECT e.id, e.name, p.title, e.start_date, e.location, e.image
        FROM exhibitions e
        LEFT JOIN paintings p ON e.painting_id = p.id
    ''')
    exhibitions = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("tables.html", {
        "request": request,
        "artists": artists,
        "paintings": paintings,
        "exhibitions": exhibitions
    })

# === ARTISTS ===
@app.get("/artists")
def get_artists():
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM artists')
    artists = cursor.fetchall()
    conn.close()
    return {"artists": artists}

@app.get("/artists/form", response_class=HTMLResponse)
async def artists_form(request: Request):
    return templates.TemplateResponse("artists_form.html", {"request": request})

@app.post("/artists")
async def add_artist(
    name: str = Form(...), 
    birth_year: int = Form(...), 
    country: str = Form(...),
    image: str = Form(default='default_artist.jpg')
):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO artists (name, birth_year, country, image) VALUES (?, ?, ?, ?)', 
                   (name, birth_year, country, image))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tables", status_code=303)

# === PAINTINGS ===
@app.get("/paintings")
def get_paintings():
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM paintings')
    paintings = cursor.fetchall()
    conn.close()
    return {"paintings": paintings}

@app.get("/paintings/form", response_class=HTMLResponse)
async def paintings_form(request: Request):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM artists')
    artists = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("paintings_form.html", {"request": request, "artists": artists})

@app.post("/paintings")
async def add_painting(
    title: str = Form(...), 
    artist_id: int = Form(...), 
    year: int = Form(...), 
    style: str = Form(...),
    image: str = Form(default='default_painting.jpg')
):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO paintings (title, artist_id, year, style, image) VALUES (?, ?, ?, ?, ?)', 
                   (title, artist_id, year, style, image))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tables", status_code=303)

# === EXHIBITIONS ===
@app.get("/exhibitions")
def get_exhibitions():
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM exhibitions')
    exhibitions = cursor.fetchall()
    conn.close()
    return {"exhibitions": exhibitions}

@app.get("/exhibitions/form", response_class=HTMLResponse)
async def exhibitions_form(request: Request):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM paintings')
    paintings = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("exhibitions_form.html", {"request": request, "paintings": paintings})

@app.post("/exhibitions")
async def add_exhibition(
    name: str = Form(...), 
    painting_id: int = Form(...), 
    start_date: str = Form(...), 
    location: str = Form(...),
    image: str = Form(default='default_exhibition.jpg')
):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO exhibitions (name, painting_id, start_date, location, image) VALUES (?, ?, ?, ?, ?)', 
                   (name, painting_id, start_date, location, image))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tables", status_code=303)

# === СТАТИСТИКА С ВИЗУАЛОМ ===
@app.get("/stats/paintings-by-artist", response_class=HTMLResponse)
async def paintings_by_artist(request: Request):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.name, a.image, COUNT(p.id) as painting_count, 
               GROUP_CONCAT(p.title, ', ') as painting_titles
        FROM artists a
        LEFT JOIN paintings p ON a.id = p.artist_id
        GROUP BY a.id, a.name, a.image
        ORDER BY painting_count DESC
    ''')
    result = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "title": "Картины по художникам",
        "data": result,
        "type": "artist"
    })

@app.get("/stats/paintings-by-style", response_class=HTMLResponse)
async def paintings_by_style(request: Request):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.style, p.image, COUNT(*) as count,
               GROUP_CONCAT(p.title, ', ') as painting_titles
        FROM paintings p
        GROUP BY p.style
        ORDER BY count DESC
    ''')
    result = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "title": "Картины по стилям",
        "data": result,
        "type": "style"
    })

@app.get("/stats/exhibitions-by-location", response_class=HTMLResponse)
async def exhibitions_by_location(request: Request):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.location, e.image, COUNT(*) as exhibition_count,
               GROUP_CONCAT(e.name, ', ') as exhibition_names
        FROM exhibitions e
        GROUP BY e.location
        ORDER BY exhibition_count DESC
    ''')
    result = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "title": "Выставки по локациям",
        "data": result,
        "type": "location"
    })

@app.get("/stats/artist-exhibitions", response_class=HTMLResponse)
async def artist_exhibitions(request: Request):
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.name, a.image, COUNT(DISTINCT e.id) as exhibition_count,
               GROUP_CONCAT(DISTINCT e.name, ', ') as exhibition_names
        FROM artists a
        LEFT JOIN paintings p ON a.id = p.artist_id
        LEFT JOIN exhibitions e ON p.id = e.painting_id
        GROUP BY a.id, a.name, a.image
        ORDER BY exhibition_count DESC
    ''')
    result = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "title": "Выставки художников",
        "data": result,
        "type": "artist_exhibitions"
    })

# === ЭКСПОРТ/ИМПОРТ JSON ===
@app.get("/export/artists/json")
def export_artists_json():
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM artists')
    artists = cursor.fetchall()
    conn.close()
    
    artists_json = []
    for artist in artists:
        artists_json.append({
            "id": artist[0],
            "name": artist[1],
            "birth_year": artist[2],
            "country": artist[3],
            "image": artist[4]
        })
    
    with open('artists_export.json', 'w', encoding='utf-8') as f:
        json.dump(artists_json, f, ensure_ascii=False, indent=2)
    
    return {"message": "Artists exported to artists_export.json", "count": len(artists_json), "data": artists_json}

@app.get("/export/paintings/json")
def export_paintings_json():
    conn = sqlite3.connect('painting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM paintings')
    paintings = cursor.fetchall()
    conn.close()
    
    paintings_json = []
    for painting in paintings:
        paintings_json.append({
            "id": painting[0],
            "title": painting[1],
            "artist_id": painting[2],
            "year": painting[3],
            "style": painting[4],
            "image": painting[5]
        })
    
    with open('paintings_export.json', 'w', encoding='utf-8') as f:
        json.dump(paintings_json, f, ensure_ascii=False, indent=2)
    
    return {"message": "Paintings exported to paintings_export.json", "count": len(paintings_json), "data": paintings_json}

@app.get("/import/form", response_class=HTMLResponse)
async def import_form(request: Request):
    return templates.TemplateResponse("import_form.html", {"request": request})

@app.post("/import/artists/json")
async def import_artists_json():
    try:
        if not os.path.exists('artists_import.json'):
            return {"error": "File artists_import.json not found. Please create it first."}
        
        with open('artists_import.json', 'r', encoding='utf-8') as f:
            artists_data = json.load(f)
        
        conn = sqlite3.connect('painting.db')
        cursor = conn.cursor()
        
        count = 0
        for artist in artists_data:
            cursor.execute('INSERT INTO artists (name, birth_year, country, image) VALUES (?, ?, ?, ?)',
                         (artist.get('name'), artist.get('birth_year'), artist.get('country'), 
                          artist.get('image', 'default_artist.jpg')))
            count += 1
        
        conn.commit()
        conn.close()
        
        return {"message": f"Successfully imported {count} artists", "count": count}
    except Exception as e:
        return {"error": str(e)}

@app.post("/import/paintings/json")
async def import_paintings_json():
    try:
        if not os.path.exists('paintings_import.json'):
            return {"error": "File paintings_import.json not found. Please create it first."}
        
        with open('paintings_import.json', 'r', encoding='utf-8') as f:
            paintings_data = json.load(f)
        
        conn = sqlite3.connect('painting.db')
        cursor = conn.cursor()
        
        count = 0
        for painting in paintings_data:
            cursor.execute('INSERT INTO paintings (title, artist_id, year, style, image) VALUES (?, ?, ?, ?, ?)',
                         (painting.get('title'), painting.get('artist_id'), painting.get('year'), 
                          painting.get('style'), painting.get('image', 'default_painting.jpg')))
            count += 1
        
        conn.commit()
        conn.close()
        
        return {"message": f"Successfully imported {count} paintings", "count": count}
    except Exception as e:
        return {"error": str(e)}