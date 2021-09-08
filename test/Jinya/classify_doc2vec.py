
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from sklearn.cluster import KMeans
import sys
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('/Users/jinya/Desktop/fav-reco/test/Jinya/data/aozora.csv')
titles = df["title"]

# モデルを読み込む
# モデルは絶対パスで指定してください
m = Doc2Vec.load('/Users/jinya/Desktop/fav-reco/test/Jinya/models/Doc2Vec_window8.model')

# ベクトルをリストに格納
vectors_list = [m.docvecs[n] for n in range(len(m.docvecs))]

# ドキュメント番号のリスト
doc_nums = range(len(m.docvecs))
print(doc_nums)

# クラスタリング設定
# クラスター数を変えたい場合はn_clustersを変えてください
n_clusters = 8
kmeans_model = KMeans(n_clusters=n_clusters, verbose=1,
                      random_state=1, n_jobs=-1)

# クラスタリング実行
kmeans_model.fit(vectors_list)

# クラスタリングデータにラベル付け
labels = kmeans_model.labels_

# ラベルとドキュメント番号の辞書づくり
cluster_to_docs = defaultdict(list)
for cluster_id, doc_num in zip(labels, doc_nums):
    cluster_to_docs[cluster_id].append(titles[doc_num])

# クラスター出力
for docs in cluster_to_docs.values():
    print(docs)

# どんなクラスタリングになったか、棒グラフ出力しますよ

# x軸ラベル
x_label_name = []
for i in range(n_clusters):
    x_label_name.append("Cluster"+str(i))

# x=left ,y=heightデータ. ここではx=クラスター名、y=クラスター内の文書数
left = range(n_clusters)
height = []
for docs in cluster_to_docs.values():
    height.append(len(docs))

# 棒グラフ設定
plt.bar(left, height, color="#FF5B70", tick_label=x_label_name, align="center")
plt.title("Document clusters")
plt.xlabel("cluster name")
plt.ylabel("number of documents")
plt.grid(True)
plt.show()
