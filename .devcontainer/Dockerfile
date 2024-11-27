# ベースイメージにUbuntuを使用
FROM ubuntu:22.04

# 必要なパッケージをインストール（非対話モードに設定）
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    git \
    curl \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0 \
    python3-gi \
    python3-gi-cairo \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# デフォルトのPythonを3.9に設定
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# 作業ディレクトリを設定
WORKDIR /workspace

# ローカルのrequirements.txtをコンテナ内にコピー
COPY requirements.txt ./

# Pythonのパッケージをインストール
RUN pip3 install --no-cache-dir -r requirements.txt

# 追加のライブラリをインストール
RUN pip3 install --no-cache-dir \
    flask \
    faiss-cpu \
    pandas \
    matplotlib \
    "langchain==0.1.20" \
    "langchain-community==0.0.38" \
    "langchain-core==0.1.52" \
    "langchain-openai==0.1.7" \
    "langchain-text-splitters==0.0.2"

# Gitリポジトリをクローン
RUN git clone https://github.com/SakutoHata/president-bot_RAG.git /app/repository

# コンテナ内の5000番ポートを開放
EXPOSE 5000
