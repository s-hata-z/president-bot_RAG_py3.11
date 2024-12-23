import numpy as np
from numpy.linalg import norm
import shutil
import ast
import os
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

def search_Index(user_query):
    similarities = []
    user_query = np.array(user_query, dtype=float)  # user_queryを数値ベクトルに変換

    for v in df["Vector"]:
        # 文字列として保存されているベクトルをリストに変換
        if isinstance(v, str):
            vec = np.array(ast.literal_eval(v), dtype=float)
        else:
            vec = np.array(v, dtype=float)

        # コサイン類似度を計算
        sim = cosine_similarity(user_query, vec)
        similarities.append(sim)

    # DataFrameに類似度カラムを追加
    df["similarity"] = similarities

    # 類似度の高い上位5件を取得
    top_5 = df.sort_values(by="similarity", ascending=False).head(5)
    return top_5["Contents"].tolist()