# ベースイメージにUbuntuを使用
FROM ubuntu:22.04

# Python と pip のインストール
RUN apt-get update && apt-get install -y python3.11 python3-pip python3.11-venv

# 作業ディレクトリを設定
WORKDIR /app

# Python仮想環境の作成
RUN python3.11 -m venv /app/venv

# 仮想環境をアクティブにする
ENV PATH="/app/venv/bin:$PATH"

# requirements.txt を先にコピー（キャッシュの活用）
COPY requirements.txt ./

# Pythonライブラリのインストール
RUN pip install --no-cache-dir -r requirements.txt

# スクリプト全体をコピー
COPY . .

# コンテナ内の5000番ポートを開放
EXPOSE 5000
