from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import urllib.parse
import mimetypes
import pathlib
import json
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('./error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)

        username = parsed_data.get('username', [''])[0]
        message = parsed_data.get('message', [''])[0]

        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Stworzenie słownika z danymi
        data_dict = {'username': username,
                     'message': message, 'timestamp': current_datetime}
        # data_dict = {
        # key: value for key, value in [el.split('=') for el in data_parse.split('&')]
        # }
        with open('data.json', 'w') as json_file:
            json.dump(data_dict, json_file)

            # print(f"Otrzymano dane: {json_data}")

        # except json.JSONDecodeError as e:
        #     print(f"Błąd dekodowania danych JSON: {e}")
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
