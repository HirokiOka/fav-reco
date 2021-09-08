# 必要なライブラリをインポート
from bs4 import BeautifulSoup
import requests
import jaconv
from gensim import corpora
from gensim import models
import pandas as pd
import string
import MeCab
import unicodedata
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import os
import re
import tweepy as tp
from dotenv import load_dotenv



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


# 青空文庫の情報をスクレイピングして、テーブルデータに整形する処理を行う関数を定義します。  
# 引数に指定した数のタイトルを出力します。(デフォルトは30)  
# 中でsymbol_removal関数を使用しています。
def Aozora_table(n=30):
    url = "https://www.aozora.gr.jp/access_ranking/2019_xhtml.html"
    res = requests.get(url)
    res.encoding = 'shift-jis'
    soup = BeautifulSoup(res.content, "html.parser")

    url_list = [url["href"] for i, url in enumerate(soup.find_all("a", target="_blank")) if i < n]

    title = []
    category = []
    text = []
    for url in url_list:
        res = requests.get(url)
        url_start = url[:37]
        res.encoding = 'shift-jis'
        soup = BeautifulSoup(res.content, "html.parser")
        for i, a in enumerate(soup.find_all("a")):
            if i == 7:
                url_end = a["href"][1:]
        url = url_start + url_end
        res = requests.get(url)
        res.encoding = 'shift-jis'
        soup = BeautifulSoup(res.content, "html.parser")
        title.append(soup.find("h1").string)
        category.append(soup.find("h2").string)
        for tag in soup.find_all(["rt", "rp"]):
            tag.decompose()
        soup = soup.find("div",{'class': 'main_text'}).get_text()
        text.append(symbol_removal(soup))
    df = pd.DataFrame({'title': title, 'category': category, 'text': text})
    return df

def get_favs(user_id, df):
    load_dotenv()
    CONSUMER_API_KEY = os.environ.get("CONSUMER_API_KEY")
    CONSUMER_SECRET_API_KEY = os.environ.get("CONSUMER_SECRET_API_KEY")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
    auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tp.API(auth)

    fav_tweets = api.favorites(user_id, count=100)

    url_pattern = re.compile("https://")
    fav_tweets_text = [fav_tweet.text for fav_tweet in fav_tweets if not url_pattern.search(fav_tweet.text)]
    fav_tweets_text = symbol_removal("".join(fav_tweets_text))
    fav_row =  pd.Series([user_id, "likes", fav_tweets_text], index=df.columns)
    print(fav_row)
    return fav_row

# 分かち書きされた2階層の単語のリストを渡すことで、TF-IDFでソートされたユニークな単語のリストを得る。
def sortedTFIDF(sentences):

    # 単語にIDを添付します。
    dictionary = corpora.Dictionary(sentences)

    # 作品ごとの単語の出現回数をカウント
    corpus = list(map(dictionary.doc2bow, sentences))

    # 単語ごとにTF-IDFを算出
    test_model = models.TfidfModel(corpus)
    corpus_tfidf = test_model[corpus]

    # ID:TF-IDF → TF-IDF:単語 に変換。TF-IDFを左に持ってくることで、sortedを用いてTF-IDFを基準にソートすることができます。
    texts_tfidf = []
    for doc in corpus_tfidf:
        text_tfidf = []
        for word in doc:
            text_tfidf.append([word[1], dictionary[word[0]]])
        texts_tfidf.append(text_tfidf)

    # TF-IDFを基準にソートを行います。
    sorted_texts_tfidf = []
    for text in texts_tfidf:
        sorted_text = sorted(text, reverse=True)
        sorted_texts_tfidf.append(sorted_text)

    return sorted_texts_tfidf


# df = Aozora_table(50)
df = pd.read_csv('/Users/jinya/Desktop/fav-reco/test/Jinya/data/aozora.csv')
# fav_row = get_favs("@j_sl_y", df)
# df = df.append(fav_row, ignore_index=True)
texts = []
for i in range(len(df)):
    texts.append(MecabMorphologicalAnalysis(df['text'][i], mecab=wakati))

# リストに変換
sentences = []
for text in texts:
    text_list = text.split(' ')
    sentences.append(text_list)

# 自作のsortedTFIDF関数を用いてTF-IDF順にソートされたリストを得る。
# sorted_texts_tfidf = sortedTFIDF(sentences)

# all_title = []
# for tfidf in sorted_texts_tfidf:
#     title = []
#     for word in tfidf[:100]: # 100語に絞る
#         title.append(word[1])
#     all_title.append(title)

# Doc2Vecモデルに重要単語リストall_titleを渡します。
documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(sentences)]
model = Doc2Vec(documents, vector_size=100, window=8, min_count=1)
model.save("Doc2Vec_window8.model")

# 結果と照らし合わせやすいように、番号と作品の一覧を表示
# for i, doc in enumerate(documents):
#     print(doc[1], df['title'][i], df['category'][i], doc[0][:8])

# ranking = model.docvecs.most_similar(50, topn=5) 
# print(ranking)
# for sim in ranking[:5]:
#     print(df['title'][sim[0]])

