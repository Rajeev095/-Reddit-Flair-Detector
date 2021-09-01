#importing libraries
import os
import numpy as np
import flask
from flask import jsonify
import pickle
from flask import Flask, render_template, request
import praw
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Use pickle to load in the pre-trained model.
loaded_model = pickle.load(open("model/tmodel.pkl", 'rb'))

reddit = praw.Reddit(client_id='R30fcxAZLJ7Wyw',
                     client_secret='8Zf87krHYa_zXRXPWEF8hK2Twfs',
                     user_agent='project1',
                     username = 'gbatra'
                    )

flairs={0:'Politics',1:'Non-Political',2:'AskIndia', 3:"[R]eddiquette", 4:'Science/Technology', 5:'Policy/Economy', 6:'Business/Finance', 7:'Scheduled', 8:'Sports', 9:'Food', 10:'Photography', 11:'AMA', 12:'Coronavirus'}

def preprocess_input(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = ''
    for w in word_tokens:
        if w not in stop_words:
            if w.isalnum():
                w = w.lower()
                filtered_sentence = filtered_sentence + ' ' + w
    filtered_sentence = " ".join(filtered_sentence.split())
    return(filtered_sentence)

def detect_flair(urls,loaded_model):
    values = []
    for url in urls:
        submission = reddit.submission(url=url)

        data = {}

        data['title'] = submission.title
        data['url'] = submission.url

        # submission.comments.replace_more(limit=None)
        # comment = ''
        # for top_level_comment in submission.comments:
        #     comment = comment + ' ' + top_level_comment.body

        # data["comment"] = comment
        data['title'] = preprocess_input(data['title'])
        # data['comment'] = preprocess_input(data['comment'])
        # data['combine'] = data['title'] + ' ' + data['comment']

        values.append(flairs[loaded_model.predict([data['title']])[0]])

    return values

#creating instance of the class
app=Flask(__name__)

#to tell flask what url shoud trigger the function index()
@app.route('/' ,  methods=['GET', 'POST'])
def index():
    urls = []
    if flask.request.method == 'GET':
        return flask.render_template('index.html')

    if flask.request.method == 'POST':
        url = flask.request.form['posturl']
        urls.append(url)
        prediction = detect_flair(urls, loaded_model)
        return flask.render_template('index.html', result = str(prediction[0]))


@app.route('/automated_testing', methods = ['POST'])
def automated_testing():
    if request.method == 'POST':
        predictions = {}
        f = request.files['upload_file']
        keys = []
        if f:
            for line in f:
                line = line.decode("utf-8")
                keys.append(line.replace("\n", ""))
            preds = detect_flair(keys , loaded_model)
            predictions = dict(zip(keys, preds)) 
    return jsonify(predictions)


if __name__=='__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', debug=True)