from gensim.models.doc2vec import Doc2Vec
import pandas as pd
from dotenv import load_dotenv
import MeCab
import unicodedata
import string
import os
import re
import tweepy as tp
import pprint



# MeCabの辞書にNEologdを指定。
# mecabは携帯素解析用、wakatiは分かち書き用
mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
wakati = MeCab.Tagger("-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")

# 形態素解析を行う関数を定義
# ファイルを入力するとファイルを出力し、文字列を渡すと文字列を返します。引数fileで変更します。  
# 単に分かち書きしたいだけの場合は引数にmecab=wakatiとすると実現できます。
def MecabMorphologicalAnalysis(path='./text.txt', output_file='wakati.txt', mecab=mecab, file=False):
    mecab_text = ''
    if file:
        with open(path) as f:
            for line in f:
                mecab_text += mecab.parse(line)
        with open(output_file, 'w') as f:
            print(mecab_text, file=f)
    else:
        for path in path.split('\n'):
            mecab_text += mecab.parse(path)
        return mecab_text

# 記号文字は分析をするにあたって邪魔になるため、記号を取り除く関数を定義します。
# 下に示すAozora_table関数の中で使います。
def symbol_removal(soup):
    soup = unicodedata.normalize("NFKC", soup)
    exclusion = "「」『』【】、。・" + "\n" + "\r" + "\u3000"
    soup = soup.translate(str.maketrans("", "", string.punctuation  + exclusion))
    return soup

def get_favs(user_id):
    load_dotenv()
    CONSUMER_API_KEY = os.environ.get("CONSUMER_API_KEY")
    CONSUMER_SECRET_API_KEY = os.environ.get("CONSUMER_SECRET_API_KEY")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
    auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tp.API(auth)

    fav_tweets = api.favorites(user_id, count=50)

    url_pattern = re.compile("https://")
    fav_tweet_texts = [fav_tweet.text for fav_tweet in fav_tweets if not url_pattern.search(fav_tweet.text)]
    fav_tweet_texts = [symbol_removal(t) for t in fav_tweet_texts]
    # fav_tweets_text = symbol_removal("".join(fav_tweets_text))
    # fav_row =  pd.Series([user_id, "likes", fav_tweets_text], index=df.columns)
    return fav_tweet_texts

m = Doc2Vec.load('/Users/jinya/Desktop/fav-reco/test/Jinya/models/Doc2Vec_window8.model')

df = pd.read_csv('/Users/jinya/Desktop/fav-reco/test/Jinya/data/aozora.csv')
titles = df["title"]


tweets = get_favs("@j_sl_y")
wakati_tweets = [MecabMorphologicalAnalysis(t, mecab=wakati) for t in tweets]

# リストに変換
sentences = []
for text in wakati_tweets:
    text_list = text.split(' ')
    sentences.append(text_list)

import numpy as np
def cal_cos_similarity(q, d):
    q = np.array(q)
    d = np.array(d)
    return np.dot(q, d) / (np.linalg.norm(q) * np.linalg.norm(d))

# import matplotlib.pyplot as plt
# epochs = [5,10,15,20,30,40,50,60,75,100]
# sims = []
# for e in epochs:
#     v1 = m.infer_vector(sentences[3], epochs=e)
#     v2 = m.infer_vector(sentences[3], epochs=e)
#     sims.append(cal_cos_similarity(v1,v2))
# height = sims
# left = epochs
# plt.plot(left, height)
# plt.show()

reccomend = []
for idx, s in enumerate(sentences):
#     v1 = m.infer_vector(s, epochs=30)
#     v2 = m.infer_vector(s, epochs=30)
#     print(cal_cos_similarity(v1,v2))

    most_similar = m.docvecs.most_similar([m.infer_vector(s, epochs=40)], topn=1)
    reccomend.append([tweets[idx], titles[most_similar[0][0]]])

pprint.pprint(reccomend)