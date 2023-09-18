from flask import Flask, request, jsonify
from pycaret.classification import *
import pandas as pd
import re
from urllib import parse,request,error
from datetime import datetime

app = Flask(__name__)

# Load your trained PyCaret model
model = load_model('model2_grindwall')

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
            count += 1
    return count

def extractDF(method, path, body):
    path = parse.unquote(path)
    single_quotes = path.count("'") + body.count("'")
    double_quotes = path.count('"') + body.count('"')
    dashes = path.count('--') + body.count('--')
    braces = path.count('{') + path.count('}') + path.count('(') + body.count('{') + body.count('}') + body.count('(')
    spaces = path.count(' ') + body.count(" ")
    tags = path.count('<') + path.count('>') + body.count('<') + body.count('>')
    colons = path.count(';') + body.count(';')
    backtick = path.count('`') + body.count('`')
    bad_words_count1 = sum(1 for word in bad_words if re.search(r'\b' + re.escape(word) + r'\b', path, re.IGNORECASE))
    bad_words_count2 = sum(1 for word in bad_words if re.search(r'\b' + re.escape(word) + r'\b', body, re.IGNORECASE))
    xss_count1 = sum(1 for word in xss if re.search(r'\b' + re.escape(word) + r'\b', path, re.IGNORECASE))
    xss_count2 = sum(1 for word in xss if re.search(r'\b' + re.escape(word) + r'\b', body, re.IGNORECASE))
    bad_words_count = bad_words_count1 + bad_words_count2
    xss_count = xss_count1 + xss_count2
    xss_check = regex_xss_check(path)
    datas = [single_quotes, double_quotes, dashes, braces, spaces, tags, colons, backtick, bad_words_count, xss_check, xss_count]
    input_data = pd.DataFrame([datas], columns=['Single Quotes', 'Double Quotes', 'Dashes', 'Braces', 'Spaces', 'Tags', 'Colons', 'Backtick', 'Bad Words', 'XSS Check', 'XSS Word'])
    return input_data

def prediction(input_data):
    predictions = predict_model(model, data=input_data)
    return predictions

@app.route('/', methods=['GET', 'POST'])
def vulnerability_check():
    try:
        method = request.method
        path = request.path
        body = request.get_data().decode('utf-8')
        full_url = f'{path}'
        print(full_url)
            
        response = request.urlopen(full_url)
        content = response.read()

        input_data = extractDF(method, path, body)
        is_safe = prediction(input_data)

        if 'bad' in is_safe:
            return "Blocked by THE GRINDWALL",403
        else:
            return "Forwarded",200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)
