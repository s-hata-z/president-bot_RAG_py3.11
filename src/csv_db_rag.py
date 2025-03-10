import numpy as np
from numpy.linalg import norm
import shutil
import ast
import os
import json
import faiss
# - OPTIONS ------------------------------------------
# import nltk
# nltk.download('punkt_tab')
# from rank_bm25 import BM25Okapi
# ----------------------------------------------------
import pandas as pd
from csv_db_indexing import main as db_indexing
from dotenv import load_dotenv

load_dotenv()

# Initialize environment variables
FILE_PATH = os.environ["FILE_PATH"]

db_indexing()

csv_file = f"{FILE_PATH}/db/csv_index/vector_index.csv"
df = pd.read_csv(csv_file)

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def text2Vec(data, embedding):
  vec_data = embedding.embed_query(data)
  return vec_data

# def search_Index(user_messages, embedding):
#     similarities = []
#     user_query = text2Vec(user_messages, embedding)
#     user_query = np.array(user_query, dtype=float)  # user_queryを数値ベクトルに変換

#     for v in df["Vector"]:
#         # 文字列として保存されているベクトルをリストに変換
#         if isinstance(v, str):
#             vec = np.array(ast.literal_eval(v), dtype=float)
#             #vec = vec = np.array(json.loads(v), dtype=float)
#         else:
#             vec = np.array(v, dtype=float)

#         # コサイン類似度を計算
#         sim = cosine_similarity(user_query, vec)
#         similarities.append(sim)

#     # DataFrameに類似度カラムを追加
#     df["similarity"] = similarities

#     # 類似度の高い上位5件を取得
#     top_5 = df.sort_values(by="similarity", ascending=False).head(5)
#     return top_5["Contents"].tolist()

def search_faiss_index_with_metadata(index_path, metadata_path, query_vector, top_k=5):
    """
    FAISSインデックスを読み込み、検索し、対応するメタデータを返す
    """
    # インデックスを読み込み
    index = faiss.read_index(index_path)

    # メタデータを読み込み
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta_data = f.readlines()

    # 検索を実行
    distances, indices = index.search(query_vector, top_k)

    # 検索結果のメタデータを取得
    results = [{"distance": distances[0][i], "metadata": meta_data[indices[0][i]].strip()} for i in range(top_k)]
    return results

def search_Index(user_messages, embedding, top_k=5):
    """
    コサイン類似度を利用して検索し、対応するメタデータを返す
    """
    index_path = f"{FILE_PATH}/db/csv_index/faiss_dump/faiss_index"
    metadata_path = f"{FILE_PATH}/db/csv_index/faiss_dump/faiss_metadata.txt"
    user_query = text2Vec(user_messages, embedding)
    user_query = np.array(user_query, dtype=float)  # user_queryを数値ベクトルに変換
    # クエリベクトルを正規化
    query_vector = user_query / np.linalg.norm(user_query)

    # クエリベクトルを2次元に変換
    if len(query_vector.shape) == 1:
        query_vector = query_vector.reshape(1, -1)

    # インデックスを読み込み
    index = faiss.read_index(index_path)

    # メタデータを読み込み
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta_data = f.readlines()

    # 検索を実行
    distances, indices = index.search(query_vector, top_k)

    # 検索結果のメタデータを取得
    results = [meta_data[indices[0][i]].strip() for i in range(top_k)]
    print(f"results：{results}")
    return results

# def search_Index(user_messages, embedding, top_k=5, bm25_k=50):
#     """
#     BM25とセマンティック検索（FAISSによるコサイン類似度計算）を組み合わせた検索を行う。
    
#     手順:
#     1. メタデータ（各文書）を読み込み、BM25で候補文書を絞り込む。
#     2. ユーザクエリをベクトル化し、FAISSインデックスから候補文書の埋め込みを取得。
#     3. 取得した候補文書の埋め込みとクエリのコサイン類似度を計算し、上位 top_k 件を返す。
#     """
#     # --- BM25による候補絞り込み ---
#     metadata_path = f"{FILE_PATH}/db/csv_index/faiss_dump/faiss_metadata.txt"
#     with open(metadata_path, "r", encoding="utf-8") as f:
#         meta_data = [line.strip() for line in f.readlines()]
    
#     # nltkのpunktパッケージを利用してトークン化
#     nltk.download('punkt', quiet=True)
#     tokenized_corpus = [nltk.word_tokenize(doc) for doc in meta_data]
    
#     # BM25のインスタンスを生成し、ユーザクエリをトークン化してスコア計算
#     bm25 = BM25Okapi(tokenized_corpus)
#     tokenized_query = nltk.word_tokenize(user_messages)
#     bm25_scores = bm25.get_scores(tokenized_query)
    
#     # BM25スコアに基づいて上位bm25_k件の候補文書のインデックスを取得
#     candidate_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:bm25_k]
    
#     # --- セマンティック検索 ---
#     # ユーザクエリを埋め込みベクトルに変換し正規化
#     user_query = text2Vec(user_messages, embedding)
#     user_query = np.array(user_query, dtype=float)
#     query_vector = user_query / np.linalg.norm(user_query)
#     if len(query_vector.shape) == 1:
#          query_vector = query_vector.reshape(1, -1)
    
#     # FAISSインデックスの読み込み
#     index_path = f"{FILE_PATH}/db/csv_index/faiss_dump/faiss_index"
#     index = faiss.read_index(index_path)
    
#     # BM25で選定された候補文書の埋め込みを取得
#     candidate_embeddings = []
#     for idx in candidate_indices:
#          # FAISSのreconstruct関数で、指定インデックスのベクトルを取得
#          candidate_embeddings.append(index.reconstruct(idx))
#     candidate_embeddings = np.vstack(candidate_embeddings)
    
#     # 候補埋め込みを正規化してコサイン類似度を計算
#     candidate_embeddings_norm = candidate_embeddings / np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
#     query_norm = query_vector / np.linalg.norm(query_vector)
#     # コサイン類似度は内積で求める
#     similarities = np.dot(candidate_embeddings_norm, query_norm.T).squeeze()  # shape: (bm25_k,)
    
#     # コサイン類似度が高い順に上位 top_k 件の候補を選出
#     top_candidate_local_indices = np.argsort(similarities)[-top_k:][::-1]
    
#     # BM25の候補インデックスから最終的な文書インデックスを取得
#     final_candidate_indices = [candidate_indices[i] for i in top_candidate_local_indices]
#     results = [meta_data[i] for i in final_candidate_indices]
#     print(f"results: {results}")
#     return results