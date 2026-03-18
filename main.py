import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import datetime
import threading
from jinja2 import Environment, FileSystemLoader

lock = threading.Lock()
env = Environment(loader=FileSystemLoader('.'))
datafile = 'storage/data.json'

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
      data = self.rfile.read(int(self.headers['Content-Length']))
      data_parse = urllib.parse.unquote_plus(data.decode())
      data_dict = dict(urllib.parse.parse_qsl(data_parse, keep_blank_values=True))

      timestamp = datetime.datetime.now().isoformat()

      with lock:
        # Load existing data
        try:
            with open(datafile, 'r') as file:
                json_data = json.load(file)
        except FileNotFoundError:
            json_data = {}

        # Add new record
        json_data[timestamp] = {
            'username': data_dict.get('username'),
            'message': data_dict.get('message')
        }

        # print(json_data)

        # save data
        with open(datafile, 'w') as file:
            json.dump(json_data, file, indent=2)

      self.send_response(302)
      self.send_header('Location', '/')
      self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/read':
            self.send_messages()
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)


    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        content_type = mt[0] if mt[0] is not None else 'text/plain'
        self.send_header("Content-type", content_type)
        self.end_headers()

        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def send_messages(self):
        # Зчитування даних з файлу data.json
        with lock:
            try:
                with open(datafile, 'r') as file:
                    json_data = json.load(file)
            except FileNotFoundError:
                json_data = {}

        # Рендер шаблону з даними
        template = env.get_template('readmsg.html')
        output = template.render(messages=json_data)

        # Відправка HTML-відповіді
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print("Server started! On http://localhost:3000")
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
