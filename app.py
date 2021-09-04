import os
import re
import tweepy as tp
from rakuten_books_api import getBookInfoFromISBN
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect
app = Flask(__name__)
app.secret_key = "asPdljfaasdu3lv"

load_dotenv()
CONSUMER_API_KEY = os.environ.get("CONSUMER_API_KEY")
CONSUMER_SECRET_API_KEY = os.environ.get("CONSUMER_SECRET_API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

CALLBACK_URL = "http://127.0.0.1:8000/favorites"
# CALLBACK_URL="https://young-dawn-36523.herokuapp.com/favorites"


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/result")
def result():
    sample_isbn = "4041099153"
    book_info = getBookInfoFromISBN(sample_isbn)
    return render_template('result.html', book_info=book_info)


@app.route('/login', methods=['GET'])
def login():
    auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY, CALLBACK_URL)
    try:
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
    except tp.TweepError as e:
        print(vars(e))
    return redirect(redirect_url)


@app.route('/favorites', methods=['GET'])
def favorites():
    favorite_tweets = getFavorites()
    return render_template('favorites.html', tweets=favorite_tweets)

def getFavorites():
    verifier = request.args.get('oauth_verifier')
    auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY, CALLBACK_URL)
    token = session['request_token']
    session.pop('request_token', None)
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tp.TweepError as e:
        print(vars(e))

    api = tp.API(auth)
    user_id = api.me().screen_name
    fav_tweets = api.favorites(user_id, count=10)
    url_pattern = re.compile("https://")
    text_only_tweets = []
    for tweet in fav_tweets:
        if not(url_pattern.search(tweet.text)):
            text_only_tweets.append(tweet)
    return text_only_tweets


if __name__ == "__main__":
    app.run(debug=False, port=8000, threaded=True)
