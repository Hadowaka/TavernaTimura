
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import re

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для localhost:8000

# Конфигурация
UPLOAD_FOLDER = os.getcwd()  # Сохраняем в текущую директорию
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Макс 16 МБ

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def escape_html(text):
    if not text:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def generate_html_page(data, page_name):
    
    main_title = escape_html(data.get('mainTitle', 'Без названия'))
    
    # Постер (будет отображаться в карточке игры)
    poster = data.get('poster', {})
    poster_src = poster.get('src', '')
    poster_alt = escape_html(poster.get('alt', ''))
    poster_desc = escape_html(poster.get('description', ''))
    
    # 1. Карточки информации
    info_cards_html = ''
    for card in data.get('infoCards', []):
        info_cards_html += f'''
        <div class="info-card">
            <h3>{escape_html(card.get('title', ''))}</h3>
            <p>{escape_html(card.get('content', ''))}</p>
        </div>'''
    
    # 2. Скриншоты
    screenshots_html = ''
    if data.get('screenshots'):
        screenshots_html = '<div class="section-header">📸 Скриншоты</div><div class="screenshots-grid">'
        for ss in data['screenshots']:
            screenshots_html += f'''
            <div class="screenshot-item">
                <img src="{escape_html(ss.get('url', ''))}" alt="{escape_html(ss.get('alt', ''))}">
                <div class="screenshot-caption">{escape_html(ss.get('alt', ''))}</div>
            </div>'''
        screenshots_html += '</div>'
    
    # 3. Видео
    videos_html = ''
    if data.get('videos'):
        videos_html = '<div class="section-header">🎬 Видео</div><div class="videos-grid">'
        for video in data['videos']:
            embed_url = escape_html(video.get('embed', ''))
            if embed_url:
                videos_html += f'''
                <div class="video-item">
                    <iframe src="{embed_url}" allowfullscreen loading="lazy"></iframe>
                    <div class="video-caption">{escape_html(video.get('title', ''))}</div>
                </div>'''
        videos_html += '</div>'
    
    # 4. Персонажи
    characters_html = ''
    if data.get('characters'):
        characters_html = '<div class="section-header">⚔️ Персонажи</div><div class="characters-grid">'
        for char in data['characters']:
            characters_html += f'''
            <div class="character-card">
                <img src="{escape_html(char.get('img', ''))}" alt="{escape_html(char.get('name', ''))}" loading="lazy">
                <h4>{escape_html(char.get('name', ''))}</h4>
                <p><strong>{escape_html(char.get('role', ''))}</strong><br>{escape_html(char.get('desc', ''))}</p>
            </div>'''
        characters_html += '</div>'
    
    # 5. Ссылки
    links_html = ''
    if data.get('relatedLinks'):
        links_html = '<div class="section-header">🔗 Ссылки</div><div class="related-links">'
        for link in data['relatedLinks']:
            links_html += f'<a href="{escape_html(link.get("url", "#"))}" target="_blank" rel="noopener">{escape_html(link.get("text", ""))}</a>'
        links_html += '</div>'

    # Постер-блок (как карточка игры)
    poster_block = f'''
    <div class="game-card">
        <div class="game-card-image">
            <img src="{poster_src}" alt="{poster_alt}" loading="lazy">
        </div>
        <div class="game-card-description">
            <p>{poster_desc}</p>
        </div>
    </div>''' if poster_src else ''
    
    info_block = f'<div class="info-grid">{info_cards_html}</div>' if info_cards_html.strip() else ''

    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{escape_html(poster_desc[:160])}">
    <title>{main_title} — Таверна Тимура</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: sans-serif;
            background-color: #f5f5f5;
        }}
        header {{
            background-color: #696969;
            padding: 15px 20px;
            border-bottom: 2px solid #ccc;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .logo {{
            font-size: 24px;
            font-weight: bold;
            color: #DCDCDC;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .logo a {{
            display: flex;
            align-items: center;
            text-decoration: none;
        }}
        .logo img {{
            height: 40px;
            width: auto;
            vertical-align: middle;
            background-color: #a0a0a0;
            border: 1px solid #888;
        }}
        #menu, #menu ul {{
            list-style: none;
            border: 1px solid #A9A9A9;
            background-color: #696969;
            padding: 0;
            margin: 0;
        }}
        #menu {{
            display: flex;
            padding: 0;
        }}
        #menu li {{
            margin-right: 3px;
            border: 1px solid #ecffec;
            position: relative;
        }}
        #menu ul {{
            position: absolute;
            top: 100%;
            left: -1px;
            width: 200px;
            padding: 0;
            display: none;
            z-index: 100;
        }}
        #menu ul li {{
            float: none;
            margin: 0;
            padding: 0;
            line-height: 15px;
            border: none;
        }}
        #menu a:link, #menu a:visited {{
            display: block;
            font-family: Tahoma, sans-serif;
            font-size: 0.75em;
            font-weight: bold;
            text-align: left;
            text-decoration: none;
            color: #DCDCDC;
            padding: 8px 10px;
            white-space: nowrap;
        }}
        #menu li:hover {{
            background-color: #FFF8DC;
            border: 1px solid #000;
        }}
        #menu li:hover ul {{
            display: block;
        }}
        #menu ul li:hover {{
            background-color: #708090;
            border: 1px solid #000;
        }}
        #menu ul li a {{
            border: none;
        }}
        .search {{
            margin-left: 10px;
            flex-shrink: 0;
            flex-grow: 1;
            min-width: 120px;
            width: auto;
        }}
        .search input {{
            padding: 6px 15px;
            border: 2px solid #A9A9A9;
            border-radius: 20px;
            background-color: #DCDCDC;
            color: #fff;
            font-size: 14px;
            width: 100%;
            box-sizing: border-box;
            transition: all 0.3s;
        }}
        .search input:hover {{
            background-color: #909090;
            border-color: #FFF8DC;
        }}
        .search input:focus {{
            outline: none;
            background-color: #fff;
            color: #333;
            border-color: #ffd98a;
            box-shadow: 0 0 5px #ffd98a;
        }}
        .forum {{
            margin-left: 10px;
            background-color: #696969;
            font-weight: bold;
            flex-shrink: 0;
        }}
        .forum a {{
            color: #DCDCDC;
            text-decoration: none;
            font-size: 1.5rem;
            line-height: 1;
        }}
        .forum a:hover {{
            color: #ffd98a;
        }}
        .office-link a {{
            color: #DCDCDC;
            text-decoration: none;
            font-weight: 500;
        }}
        .office-link a:hover {{
            color: #ffd98a;
            text-decoration: underline;
        }}
        .office-link {{
            margin-left: 10px;
            background-color: #696969;
            flex-shrink: 0;
        }}
        .Oschimdaemie_igri {{
            background-color: #DCDCDC;
            padding: 4px 20px;
            border-bottom: 2px solid #D3D3D3;
            display: flex;
            align-items: center;
            gap: 15px;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            margin-bottom: 15px;
            margin-top: 30px;
        }}
        .Oschimdaemie_igri span {{
            font-weight: bold;
            color: #333;
            flex-shrink: 0;
        }}
        main {{
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            min-height: 200px;
        }}
        @media (max-width: 900px) {{
            .search {{ max-width: none; width: 100%; }}
        }}
        @media (max-width: 700px) {{
            header {{ flex-wrap: wrap; }}
            .search {{ margin-left: 0; width: 100%; max-width: none; }}
            #menu {{ flex-wrap: wrap; }}
        }}
        
        /* Стили для карточки игры */
        .game-card {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            align-items: flex-start;
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 16px;
            border-left: 4px solid #696969;
        }}
        .game-card-image {{
            flex-shrink: 0;
        }}
        .game-card-image img {{
            width: 220px;
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            object-fit: cover;
        }}
        .game-card-description {{
            flex: 1;
            font-style: italic;
            color: #555;
            min-width: 250px;
        }}
        
        /* Стили для информационных карточек */
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .info-card {{
            background: #f8f9fa;
            border-left: 4px solid #696969;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
        }}
        .info-card h3 {{
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        /* Стили для секций */
        .section-header {{
            background: linear-gradient(135deg, #696969 0%, #808080 100%);
            color: #fff;
            padding: 12px 20px;
            border-radius: 10px;
            margin: 40px 0 20px;
            font-weight: 600;
            font-size: 1.2em;
        }}
        
        /* Сетка скриншотов */
        .screenshots-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .screenshot-item img {{
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .screenshot-item img:hover {{
            transform: scale(1.03);
        }}
        .screenshot-caption {{
            text-align: center;
            font-size: 0.9em;
            color: #666;
            margin-top: 8px;
        }}
        
        /* Сетка видео */
        .videos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .video-item {{
            background: #f8f9fa;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        }}
        .video-item iframe {{
            width: 100%;
            aspect-ratio: 16/9;
            border: none;
        }}
        .video-caption {{
            padding: 10px 15px;
            text-align: center;
            font-weight: 500;
            background: #fff;
        }}
        
        /* Сетка персонажей */
        .characters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .character-card {{
            background: #fff8e1;
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }}
        .character-card:hover {{
            transform: translateY(-3px);
        }}
        .character-card img {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 12px;
            border: 3px solid #fff;
            box-shadow: 0 3px 8px rgba(0,0,0,0.15);
        }}
        .character-card h4 {{
            color: #2c3e50;
            margin: 8px 0 4px;
        }}
        .character-card p {{
            font-size: 0.9em;
            color: #666;
        }}
        
        /* Ссылки */
        .related-links {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 12px;
            margin: 20px 0;
        }}
        .related-links a {{
            display: inline-block;
            margin: 5px 10px 5px 0;
            background: #696969;
            color: #fff;
            padding: 8px 16px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 0.95em;
            transition: all 0.2s;
        }}
        .related-links a:hover {{
            background: #ffd98a;
            color: #1e1e1e;
            transform: translateY(-2px);
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #eee;
            margin-top: 40px;
        }}
        
        @media (max-width: 768px) {{
            .game-card {{
                flex-direction: column;
                align-items: center;
                text-align: center;
            }}
            .screenshots-grid, .characters-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .videos-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        @media (max-width: 480px) {{
            .screenshots-grid, .characters-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <a href="TavernaTimur.html">
                <img src="Logo.jpg" alt="Таверна Тимы — логотип">
            </a>
            <span>Таверна Тимы</span>
        </div>
        <ul id="menu">
            <li><a href="#">Игры</a>
                <ul>
                    <li><a href="#">Ожидаемые игры</a></li>
                    <li><a href="#">Игроновости</a></li>
                    <li><a href="#">Каталог игр</a></li>
                    <li><a href="#">Ретро-спектива</a></li>
                    <li><a href="#">И ещё</a></li>
                    <li><a href="#">И тут что-то ещё</a></li>
                    <li><a href="#">Тимур</a></li>
                </ul>
            </li>
            <li><a href="#">Сообщество</a>
                <ul>
                    <li><a href="#">Форум</a></li>
                    <li><a href="https://www.woman.ru/forum/">Вумен ру</a></li>
                    <li><a href="#">Форум по доте</a></li>
                    <li><a href="#">Создать форум</a></li>
                </ul>
            </li>
            <li><a href="#">Разное</a></li>
        </ul>
        <div class="search">
            <input type="text" placeholder="🔍 Поиск по сайту...">
        </div>
        <div class="forum"><a href="te.html">💬</a></div>
        <div class="office-link"><a href="TavernaTimurReg.html">Личный кабинет</a></div>
    </header>

    <div class="Oschimdaemie_igri"><span>{main_title}</span></div>
    
    <main>
        {poster_block}
        {info_block}
        {screenshots_html}
        {videos_html}
        {characters_html}
        {links_html}
    </main>
    
    <footer>
        <p>© {page_name} — Создано в Таверне Тимура</p>
    </footer>
</body>
</html>'''

@app.route('/create_game_page', methods=['POST'])
def create_game_page():
    try:
        # Получаем данные формы
        page_name = request.form.get('page_name', '').strip()
        data_json = request.form.get('data', '{}')
        
        # Валидация названия
        if not page_name or not re.match(r'^[a-zA-Z0-9_]+$', page_name):
            return jsonify({
                'success': False,
                'message': 'Название должно содержать только латинские буквы, цифры и подчёркивания'
            }), 400
        
        # Парсим JSON
        try:
            page_data = json.loads(data_json)
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'message': f'Ошибка JSON: {str(e)}'}), 400
        
        # Создаём структуру папок
        game_folder = os.path.join(UPLOAD_FOLDER, page_name)
        media_folder = os.path.join(game_folder, 'media')
        os.makedirs(media_folder, exist_ok=True)
        
        # Обработка файлов 
        
        # Постер
        if 'poster' in request.files:
            poster_file = request.files['poster']
            if poster_file and poster_file.filename and allowed_file(poster_file.filename):
                filename = secure_filename(poster_file.filename)
                poster_path = os.path.join(media_folder, filename)
                poster_file.save(poster_path)
                page_data.setdefault('poster', {})['src'] = f'media/{filename}'
        
        # Скриншоты
        for key in request.files:
            if key.startswith('screenshot_'):
                file = request.files[key]
                if file and file.filename and allowed_file(file.filename):
                    idx = key.split('_')[1]
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(media_folder, filename)
                    file.save(file_path)
                    screenshots = page_data.get('screenshots', [])
                    if int(idx) < len(screenshots):
                        screenshots[int(idx)]['url'] = f'media/{filename}'
        
        # Персонажи
        for key in request.files:
            if key.startswith('character_'):
                file = request.files[key]
                if file and file.filename and allowed_file(file.filename):
                    idx = key.split('_')[1]
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(media_folder, filename)
                    file.save(file_path)
                    characters = page_data.get('characters', [])
                    if int(idx) < len(characters):
                        characters[int(idx)]['img'] = f'media/{filename}'
        
        # Сохранение JSON 
        json_path = os.path.join(game_folder, f'{page_name}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        
        # Генерация HTML 
        html_content = generate_html_page(page_data, page_name)
        html_path = os.path.join(game_folder, f'{page_name}.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        

        source_file = 'Saytik/Logo.jpg'  
        destination_dir = page_name  

        shutil.copy(source_file, destination_dir)

        
        # Успешный ответ
        return jsonify({
            'success': True,
            'message': f'Страница "{page_name}" успешно создана!',
            'path': os.path.abspath(game_folder),
            'page_name': page_name,
            'files': {
                'json': f'{page_name}.json',
                'html': f'{page_name}.html',
                'media_folder': 'media/'
            }
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Ошибка: {e}\n{error_details}")
        return jsonify({
            'success': False,
            'message': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'Generator_page_games'})

if __name__ == '__main__':
    print(" Порт: 8001")
    print("CORS разрешён для: http://localhost:8000")
    print("Папка сохранения: " + UPLOAD_FOLDER)
    print("Проверка: http://localhost:8001/health")
    print("Остановка: Ctrl+C")
    print("="*50)
    
    app.run(
        host='127.0.0.1',
        port=8001,
        debug=True,
        threaded=True
    )
