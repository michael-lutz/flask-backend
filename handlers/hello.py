from http.server import BaseHTTPRequestHandler
import os
import openai
import json
import ast

openai.api_key = os.getenv("OPENAI_API_KEY")

class handler(BaseHTTPRequestHandler):
    # Write a post method that handles a request wih the parameter "input" and writes the value of input
    def do_POST(self):
        content_length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_length)
        print(body.decode('utf-8'))
        content = ast.literal_eval(body.decode('utf-8'))
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        res = content['input']
        d = {'message': res}
        res_body = json.dumps(d)
        # stringify the json
        self.wfile.write(res_body.encode())
