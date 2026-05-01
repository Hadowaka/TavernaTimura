import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class GamePageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            with open('editor.html', 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/save_game_json':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                page_name = data.get('page_name', '').strip()
                page_data = data.get('data', {})
                
                if not page_name:
                    self.send_json_response({'success': False, 'message': 'Название страницы не может быть пустым'})
                    return
                
                # Проверяем существование папки
                if os.path.exists(page_name):
                    self.send_json_response({'success': False, 'message': f'Папка "{page_name}" уже существует!'})
                    return
                
                # Создаем папку
                os.mkdir(page_name)
                
                # Переходим в папку
                os.chdir(page_name)
                
                # Сохраняем JSON файл
                json_filename = f"{page_name}.json"
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, ensure_ascii=False, indent=2)
                
                # Возвращаемся обратно
                os.chdir('..')
                
                self.send_json_response({
                    'success': True,
                    'message': f'Папка "{page_name}" и файл "{json_filename}" успешно созданы',
                    'path': os.path.abspath(page_name)
                })
                
            except Exception as e:
                self.send_json_response({'success': False, 'message': f'Ошибка: {str(e)}'})
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json_response(self, response):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, GamePageHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
