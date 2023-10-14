from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
from threading import Thread
import json
from datetime import datetime

FILE = "./storage/data.json"
UDP_IP = '127.0.0.1'
UDP_PORT = 5000

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
                self.send_html_file('error.html', 404)

    # Для відповіді браузеру ми використовуємо метод send_html_file
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

# Обробка форми виконується функцією do_POST.
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        # print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        # print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        run_client(UDP_IP, UDP_PORT, data_dict)


def run_client(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    values = str((data.values()))
    print(f"values:{values}")
    # sock.sendto(keys.encode(), server)
    sock.sendto(values.encode(), server)
    sock.close()


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')
            data_tuple = tuple(data)
            print(f"data_tuple:{data_tuple}")
            # save_message(username, message)
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def save_message(username, message):
    try:
        with open(FILE, "r+") as fh:
            data = json.loads(fh.read())
            data[str(datetime.now())] = {"username": username, 'message': message}
            fh.seek(0)
            fh.write(json.dumps(data))
    except FileNotFoundError:
        pathlib.Path("./storage/").mkdir(exist_ok=True)
        with open(FILE, "w") as fh:
            fh.write(json.dumps({}))
        save_message(username, message)


if __name__ == '__main__':
    http_server = Thread(target=run)
    socket_server = Thread(target=run_server, args=(UDP_IP, UDP_PORT))
    http_server.start()
    socket_server.start()

    #
    # run()
    # echo_server("", 5000)