import json
import os
import random
import time
from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'árvíztükörfúrógép'

WORD_DICTIONARY = "words.json"

@app.route("/")
def index():
    with open("index.html", "r") as f:
        html = f.read()
    return html
    
@app.route("/js/<jsFile>")
def get_JQuery(jsFile):
    with open("js/" + jsFile, "r") as f:
        html = f.read()
    return html

@app.route("/count")
def show_list():
    words = load_file(WORD_DICTIONARY)
    count_obj = { "count": len(words["ly"])  + len(words["j"])}
    return json.dumps(count_obj)
    
@app.route("/start/<name>/<count>/<test_type>")
def start_test(name, count, test_type):
    words = load_file(WORD_DICTIONARY)
    test_id = "{}{}{}".format(name, count, time.time())
    test_words = []
    all_words = words["ly"] + words["j"]
    while len(test_words) < int(count):
        test_words.append(all_words.pop(random.randrange(0, len(all_words))))
    init_session(name, count, test_type)
    return get_next_word(test_words, test_id)
    
@app.route("/next/<test_id>/<word>/<answer>")
def next_word(test_id, word, answer):
    test_words = load_file(test_id)
    if session['type'] == 'normal':
        session['points'] += 1 if check_answer(word, answer) else 0
    else:
        if not check_answer(word, answer):
            session['faults'] += 1
            test_words.append(word) 
    if len(test_words) == 0:
        os.remove(test_id) 
        results = store_result()
        results.pop(0)
        return json.dumps({"result": "{} out of {}".format(session['points'], session['count'])
            if session['type'] == 'normal' else
            "{} times failed".format(session['faults']), "previous": results})
    return get_next_word(test_words, test_id)
    

def get_next_word(test_words, test_id):
    word = test_words[0]
    test_words.pop(0)
    write_file(test_id, test_words)
    return json.dumps({"word": word, "id": test_id}, ensure_ascii=False)
    
def load_file(file_name):
    with open(file_name, 'r', encoding="utf-8") as f:
        return json.load(f)
        
def write_file(file_name, content):
    with open(file_name, 'w', encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False)
        
def check_answer(word, answer):
    words = load_file(WORD_DICTIONARY)[answer]
    return word in words

def init_session(name, count, test_type):
    session['points'] = 0
    session['faults'] = 0
    session['name'] = name
    session['count'] = count
    session['type'] = test_type
    
def store_result():
    result_file_name = "{}.res".format(session['name'])
    try:
        results = load_file(result_file_name)
    except:
        results = []
    results.insert(0, "{} out of {}".format(session['points'], session['count'])
        if session['type'] == 'normal' else
        "{} times failed".format(session['faults']))
    write_file(result_file_name, results)
    return results