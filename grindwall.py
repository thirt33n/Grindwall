from http.server import SimpleHTTPRequestHandler,HTTPServer
from urllib import request,error
import urllib.parse
import http.cookiejar
import sys
import requests
from pycaret.classification import *
import pandas as pd
import logging
import re
from datetime import datetime



nttfy_docker='https://ntfy.sh/th1rt33n'
data = 'Malicious Request Detected'

#Logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')  


model = load_model('model3_grindwall')

cookies = http.cookiejar.CookieJar()



bad_words = ['sleep', 'drop', 'uid', 'select', 'waitfor', 'delay', 'system', 'union', 'order by', 'delete', 'group by', 'insert', 'or']
xss = ['script','img','a','javascript','svg','onclick']


def regex_xss_check(path):
     
    xss_patterns = [
        r'<script\s[^>]*>[\s\S]*?<',
        r'(on\w+)=["\'](.*?)["\']',
        r'<img\s[^>]*\son\w+=["\'](.*?)["\'][^>]*>',
        r'href=["\'](javascript:[^"\']+)["\']',
        r'\bjavascript:\s*[^;]+;'
    ]
    count = 0
     

    for pattern in xss_patterns:
        if re.search(pattern, path):
            count=count+1
            

    return count





def extractDF(method,path,body):
    path = urllib.parse.unquote(path)
    single_quotes = path.count("'") + body.count("'")
    double_quotes = path.count('"') + body.count('"')
    dashes = path.count('--') + body.count('--')
    braces = path.count('{') + path.count('}') + path.count('(') + body.count('{') + body.count('}') + body.count('(')
    spaces = path.count(' ') + body.count(" ")
    tags = path.count('<') + path.count('>')+ body.count('<')+body.count('>')
    colons = path.count(';')+body.count(';')
    backtick = path.count('`')+body.count('`')
    bad_words_count1 = sum(1 for word in bad_words if re.search(r'\b' + re.escape(word) + r'\b', path, re.IGNORECASE))
    bad_words_count2 = sum(1 for word in bad_words if re.search(r'\b' + re.escape(word) + r'\b', body, re.IGNORECASE))
    xss_count1 = sum(1 for word in xss if re.search(r'\b' + re.escape(word) + r'\b', path, re.IGNORECASE))
    xss_count2 = sum(1 for word in xss if re.search(r'\b' + re.escape(word) + r'\b', body, re.IGNORECASE))
    bad_words_count = bad_words_count1+ bad_words_count2
    xss_count = xss_count1+xss_count2
    xss_check = regex_xss_check(path)
    datas = [single_quotes, double_quotes, dashes, braces, spaces,tags,colons,backtick, bad_words_count,xss_check,xss_count]
    log_data = [method,path,body]
    input = pd.DataFrame([datas], columns=['Single Quotes', 'Double Quotes', 'Dashes', 'Braces', 'Spaces','Tags','Colons','Backtick', 'Bad Words','XSS Check','XSS Word'])
    log = pd.DataFrame([log_data],columns=['Method','Path','Body'])
    return input,log

def prediction(input):
    prediction = predict_model(model,data=input)
 
    return prediction

class SimpleHttpProxy(SimpleHTTPRequestHandler):

    @classmethod
    def set_routes(cls,proxy_routes):
        cls.proxy_routes = proxy_routes

    

    def do_GET(self) -> None:
        try:
            body=''
            path = self.path
            method = self.command
            full_url = f'{path}'
            print(full_url)
            
            response = request.urlopen(full_url)
            content = response.read()

            inp,log = extractDF(method,path,body)
            
            pred = prediction(inp)

            result = pd.concat([log,pred],axis=1)

            result.to_csv('log_dataset.csv',mode='a',header=False,index=False)        


            print(pred)
            pp = pred['prediction_label'].to_string()
            
            log_message = f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - GET Prediction: {pred.to_string()}"
            logging.info(log_message)
            if 'good' in pp:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(content)
       
    		                
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Blocked by THE GRINDWALL")
                
                try:
                    resp = requests.post(nttfy_docker,data=data)
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(f"HTTP Error {resp.status_code}: {err}")
    		        
                except requests.exceptions.RequestException as err:
                     print(f"Request Error: {err}")
        except Exception as e:
            logging.error(f"Error in the GET request: str{e}")

    def do_POST(self)-> None:
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length).decode('utf-8')
            path = self.path
            method = self.command
            full_url = f'{path}'
            body = post_body
            response = request.urlopen(full_url)
            content = response.read()

            inp,log = extractDF(method,path,body)
            
            pred = prediction(inp)

            result = pd.concat([log,pred],axis=1)

            result.to_csv('log_dataset.csv',mode='a',header=False,index=False) 
        
            print(pred)
            log_message = f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - POST Prediction: {pred.to_string()}"
            logging.info(log_message)
            pp = pred['prediction_label'].to_string()
            # print(pp)
            # pred = 'bad'
            if 'good' in pp:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(content)
    		        
                
            else:
                
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Blocked by THE GRINDWALL")
                
                try:
                    resp = requests.post(nttfy_docker,data=data)
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(f"HTTP Error {resp.status_code}: {err}")
    		        
                except requests.exceptions.RequestException as err:
                    print(f"Request Error: {err}")
        except Exception as e:
            logging.error(f"Error in POST requests: {str(e)}")


if __name__ == '__main__':
    server_address = ('', 1234)
    httpd = HTTPServer(server_address, SimpleHttpProxy)
    httpd.serve_forever()
    print("Server Started on port: 1234")