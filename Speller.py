from Dictionary import Dictionary
import json
import Io
import os
import random
import time
from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'árvíztükörfúrógép'

WORD_DICTIONARY = "words.json"

dictionary = Dictionary(WORD_DICTIONARY)

@app.route("/")
def index():
    with open("index.html", "r") as f:
        html = f.read()
    return html

@app.route("/manage")
def manage():
    with open("manage.html", "r") as f:
        html = f.read()
    return html
    
@app.route("/js/<jsFile>")
def get_JQuery(jsFile):
    with open("js/" + jsFile, "r") as f:
        html = f.read()
    return html

@app.route("/dictionary/count")
def show_list():
    return dictionary.get_count()

@app.route("/dictionary")
def get_dictionary():
    return dictionary.get_word_list()
    
@app.route("/dictionary/add/<word>")
def dictionary_add(word):
    return dictionary.save_word(word)
    
@app.route("/dictionary/delete/<word>")
def dictionary_remove(word):
    dictionary.delete_word(word)
    return get_dictionary()
    
@app.route("/test/start/<name>/<count>/<test_type>")
def start_test(name, count, test_type):
    words = dictionary.get_words()
    if out_of_range(words, count):
        return json.dumps({"result": "0 out of 0"})
    test_id = "{}{}{}".format(name, count, time.time())
    test_words = create_word_list(words, count)
    init_session(name, count, test_type)
    Io.write_file(test_id, test_words)
    return get_word_at(test_words, test_id, 0)

@app.route("/test/<test_id>/word/<num>")
def word(test_id, num):
    try:
        test_words = Io.load_file(test_id)
    except Exception as e:
        return json.dumps({"error": "Failed to load test"})
    if (int(num) < len(test_words)):
        return get_word_at(test_words, test_id, int(num))
    n = get_first_error(test_words)
    if n != -1:
        return get_word_at(test_words, test_id, n)
    return json.dumps({"error": "You found a bug!"})

@app.route("/test/<test_id>/word/<num>/answer/<answer>")
def answer(test_id, num, answer):
    try:
        test_words = Io.load_file(test_id)
    except Exception as e:
        return json.dumps({"error": "Failed to load test"})
    if (int(num) < len(test_words)):
        word = json.loads(get_word_at(test_words, test_id, int(num)))
    else:
        num = get_first_error(test_words)
        if (num == -1):
            return json.dumps({"error": "You found the bug!"})
        word = json.loads(get_word_at(test_words, test_id, num))
    correct = 0
    if session['type'] == 'normal':
        if check_answer(word["word"], answer):
            session['points'] += 1
            correct = 1
    else:
        if not check_answer(word["word"], answer):
            session['faults'] += 1
        else:
            correct = 1
    test_words[int(num)][1] = correct
    test_words[int(num)][2] += 1
    Io.write_file(test_id, test_words)
    if test_finished(test_words, session['type']):
        os.remove(test_id) 
        results = store_result()
        results.pop(0)
        return json.dumps({"result": "{} out of {}".format(session['points'], session['count'])
            if session['type'] == 'normal' else
            "{} times failed".format(session['faults']), "previous": results})
    return get_word_at(test_words, test_id, int(num))
    
def create_word_list(words, count): 
    test_words = []
    all_words = words["ly"] + words["j"]
    while len(test_words) < int(count):
        test_words.append([all_words.pop(random.randrange(0, len(all_words))), 0, 0])
    return test_words

def get_word_at(test_words, test_id, num):
    word = test_words[num]
    return json.dumps({"word": word[0], "id": test_id}, ensure_ascii=False)
        
def check_answer(word, answer):
    words = dictionary.get_words()[answer]
    return word in words

def init_session(name, count, test_type):
    session['points'] = 0
    session['faults'] = 0
    session['name'] = name
    session['count'] = count
    session['type'] = test_type

def test_finished(test_words, type):
    guessed = 0
    all_correct = True
    for n in range(0, len(test_words)):
        if (test_words[n][2] > 0):
            guessed += 1
        all_correct = all_correct and test_words[n][1] == 1
    if guessed == len(test_words) and type == 'normal':
        return True
    return all_correct


def store_result():
    result_file_name = "{}.res".format(session['name'])
    try:
        results = Io.load_file(result_file_name)
    except:
        results = []
    results.insert(0, "{} out of {}".format(session['points'], session['count'])
        if session['type'] == 'normal' else
        "{} times failed".format(session['faults']))
    Io.write_file(result_file_name, results)
    return results
    
def out_of_range(words, count):
    return int(count) < 1 or int(count) > len(words["ly"])  + len(words["j"])

def get_first_error(test_words):
    n = 0
    while n < len(test_words):
        if (test_words[n][1] != 1):
            return n
        n += 1
    return -1