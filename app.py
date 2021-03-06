import os
import time
import random
import re
import string
import unicodedata
import tweepy as tp
from libs import get_book_info, aozora_api, new_recommend
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect


app = Flask(__name__)
app.secret_key = os.urandom(16)

load_dotenv()
CONSUMER_API_KEY = os.environ.get("CONSUMER_API_KEY")
CONSUMER_SECRET_API_KEY = os.environ.get("CONSUMER_SECRET_API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
APPLICATION_ID = os.environ.get("APPLICATION_ID")

# CALLBACK_URL = "http://127.0.0.1:8000/result"
CALLBACK_URL = "http://tsubuyaki-syoten.herokuapp.com/result"

path_to_dict = "./libs/data/mecab/dic/ipadic"
path_to_d2v_model = "./model/new_doc2vec_ver03.model"
path_to_aozora = "./aozora_data.csv"
path_to_dummy = "./static/img/dummy-book"
path_to_book = "./static/img/book.png"
path_to_model = "./model/new_doc2vec_ver03.model"
dummy_img = os.listdir(path_to_dummy)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/test")
def test():
    sample_titles_and_authors = {
            "人間失格": "太宰治",
            "陰翳礼讃": "谷崎潤一郎",
            "変身": "フランツ カフカ",
            "銀河鉄道の夜": "宮沢賢治",
            "風の歌を聴け": "村上春樹",
            "パプリカ": "筒井康隆"
            }
    books_info = []
    index = 0
    for book_title, author in sample_titles_and_authors.items():
        book_info = get_book_info.getBookInfoTest(book_title, author, APPLICATION_ID)
        print(book_info)
        if (book_info):
            book_info["mediumImageUrl"] = path_to_dummy + "/" + dummy_img[index]
            books_info.append(book_info)
            index += 1
        time.sleep(0.2)
    return render_template('result.html', books_info=books_info)


@app.route('/login', methods=['GET'])
def login():
    auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY, CALLBACK_URL)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    try:
        redirect_url = auth.get_authorization_url()
        redirect_http = redirect_url.replace("s", "", 1)
        session['request_token'] = auth.request_token
    except tp.TweepError as e:
        print("Tweepy Error:", vars(e))
        # return render_template("index.html")
    return redirect(redirect_http)


@app.route("/result", methods=['GET'])
def result():
    verifier = request.args.get('oauth_verifier')
    auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY, CALLBACK_URL)
    try:
        token = session['request_token']
        session.pop('request_token', None)
        auth.request_token = token
    except Exception as e:
        print(e)
        # return render_template('index.html')

    try:
        auth.get_access_token(verifier)
    except tp.TweepError as e:
        print(vars(e))
        # return render_template('index.html')

    api = tp.API(auth)
    favorite_tweets = getFavorites(api, 50)
    results = new_recommend.getMostSimilerClusterOfFavs(favorite_tweets, path_to_aozora, path_to_dict, path_to_model)
    books_info = []

    for title, author in results.items():
        print(title, author)
        book_info = get_book_info.getBookInfoFromTitle(title, APPLICATION_ID)
        if (book_info):
            books_info.append(book_info)
        else:
            book_info = aozora_api.getAozoraInfo(title)
            if (book_info):
                book_info["mediumImageUrl"] = path_to_dummy + "/" + dummy_img[random.randint(1, 5)]
                books_info.append(book_info)
            else:
                continue
        if (len(books_info) > 5):
            break
        time.sleep(0.2)
    return render_template('result.html', books_info=books_info)


def removeSymbol(text):
    text = unicodedata.normalize("NFKC", text)
    exclusion = "〔〕「」『』【】、。・" + "\n" + "\r" + "\u3000"
    text = text.translate(str.maketrans("", "", string.punctuation + exclusion))
    return text


def getFavorites(api, count=10):
    user_id = api.me().screen_name
    fav_tweets = api.favorites(user_id, count)
    url_pattern = re.compile("https://")
    text_only_tweets = []
    for tweet in fav_tweets:
        if not(url_pattern.search(tweet.text)):
            text_only_tweets.append(tweet.text)

    fav_tweet_texts = [removeSymbol(t) for t in text_only_tweets]
    return fav_tweet_texts


if __name__ == "__main__":
    app.run(debug=True, port=8000)
