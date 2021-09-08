from gensim import corpora
from gensim import models
import pandas as pd
import string
import MeCab
import unicodedata
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import os
import re

# MeCabの辞書にNEologdを指定。
# mecabは携帯素解析用、wakatiは分かち書き用
mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
wakati = MeCab.Tagger("-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")

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

df = pd.read_csv()

#わかち書き
texts = []
for i in range(len(df)):
    texts.append(MecabMorphologicalAnalysis(df['text'][i], mecab=wakati))

# リストに変換
sentences = []
for text in texts:
    text_list = text.split(' ')
    sentences.append(text_list)

documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(sentences)]
model = Doc2Vec(documents, vector_size=100, window=5, min_count=1)
model.save("test/Jinya/models/Doc2Vec.model")

