from http.server import SimpleHTTPRequestHandler,HTTPServer
from urllib import request,error
import urllib.parse
import http.cookiejar
import sys
from pycaret.classification import *
import pandas as pd
import re

model = load_model('model1_grindwall')

cookies = http.cookiejar.CookieJar()



bad_words = ['sleep', 'drop', 'uid', 'select', 'waitfor', 'delay', 'system', 'union', 'order by', 'delete', 'group by', 'insert', 'or']

def extractDF(method,path,body):
    path = urllib.parse.unquote(path)
    single_quotes = path.count("'") + body.count("'")
    double_quotes = path.count('"') + body.count('"')
    dashes = path.count('--') + body.count('--')
    braces = path.count('{') + path.count('}') + path.count('(') + body.count('{') + body.count('}') + body.count('(')
    spaces = path.count(' ') + body.count(" ")
    bad_words_count1 = sum(1 for word in bad_words if re.search(r'\b' + re.escape(word) + r'\b', path, re.IGNORECASE))
    bad_words_count2 = sum(1 for word in bad_words if re.search(r'\b' + re.escape(word) + r'\b', body, re.IGNORECASE))
    bad_words_count = bad_words_count1+ bad_words_count2
    datas = [method,path,body,single_quotes,double_quotes,dashes,braces,spaces,bad_words_count]
    input = pd.DataFrame([datas], columns=['Method','Path','Body','Single_q', 'Double_q', 'Dashes', 'Braces', 'Spaces', 'Bad_Words'])
    return input

def prediction(input):
    prediction = predict_model(model,data=input)
    # op = predict_model.loc[0,'prediction_label']
    return prediction

class SimpleHttpProxy(SimpleHTTPRequestHandler):

    @classmethod
    def set_routes(cls,proxy_routes):
        cls.proxy_routes = proxy_routes

    

    def do_GET(self) -> None:

        body=''
        path = self.path
        method = self.command
        full_url = f'{path}'
        print(full_url)
        
        response = request.urlopen(full_url)
        content = response.read()

        inp = extractDF(method,path,body)
        # print(inp)
        pred = prediction(inp)
        # grind = pred['predition_label']
        print(pred)
        pp = pred['prediction_label'].to_string()
        print(pp)
        # pred = 'bad'
        if 'bad' in pp:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Blocked by THE GRINDWALL")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(content)

    def do_POST(self)-> None:
        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length).decode('utf-8')
        path = self.path
        method = self.command
        full_url = f'{path}'
        body = post_body
        response = request.urlopen(full_url)
        content = response.read()

        inp = extractDF(method,path,body)
       
        pred = prediction(inp)
       
        print(pred)
        pp = pred['prediction_label'].to_string()
        print(pp)
        # pred = 'bad'
        if 'bad' in pp:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Blocked by THE GRINDWALL")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(content)


if __name__ == '__main__':
    server_address = ('', 1234)
    httpd = HTTPServer(server_address, SimpleHttpProxy)
    httpd.serve_forever()
    print("Server Started on port: 1234")
