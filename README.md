# 社長ボット

## はじめに
インターンでPoCのため、作成いたしました。<br>
3Dモデルとコミュニケーション可能なかつ、RAG構成のフロントおよびバックエンドを構築したWebアプリです。当リポジトリではアプリのみの解説を行っております。

## プロジェクト開始時点の要求
- Microsoft Teamsで動作可能なこと
- Webアプリの構築も同時に行ってほしい
- 対話しているように感じることのできるUIにしてほしい（VRみたいな感じ）
- 性能のよい生成AIを使いたい（当時ではOpenAI系モデルがトップだった...）
- AWSとAzureOpenAIを組み合わせることができるか検証してほしい
- 社長が執筆した文書をナレッジとしたチャットボットが欲しい（CSVデータ）

## システム構成
#### Teams対応版
![ボット構成図](/images/ボット構成図.jpg)<br>
基本的に、AzureOpenAIとAWSのEC2を接続する構成となっています。<br>
AWS Certificate Managerでドメインを取得し、ALBにアタッチする形でレコードを作成することで、WAFを通じてアクセス可能なデバイス側のIPアドレスを制限しました。

## セットアップ
### 1. EC2の設定（初回のみ）
- アプリケーションおよびOSイメージ：Ubuntu
- インスタンスタイプ：t2.small
- セキュリティグループ：Azure側（OpenAIのエンドポイント）、VSCode側（Flask）と通信可能にしておく
- キーペア：新規作成して下さい。ここで生成されたkeyファイルは開発用PCの".sshフォルダ"に格納し、VSCodeのリモート開発機能等を使って当リポジトリを導入してください。

※ElasticIPの割り当て、ドメイン発行、WAFの適応はここでは紹介しないが行っておくこと。

### 2. ローカル環境構築（初回のみ）
初回で必須の対応となります。<br>
初回以降は、「[5.環境変数](#5-環境変数毎回行うこと)」→ 「[6.アプリの起動](#6アプリの起動毎回行うこと)」の順で実行して下さい。

1. EC2をLinux/Ubuntu で構築

2. terminalで以下を実行
    ```
    sudo update -y
    sudo apt update
    sudo apt install python3 -y
    sudo apt install python3-pip -y
    sudo apt install git
    sudo apt install build-essential -y
    sudo apt install zlib1g-dev libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libgdbm-dev liblzma-dev -y
    ```

3. pythonのバージョン指定
    ```
    sudo apt update
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.9 python3.9-venv python3.9-dev
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2
    sudo update-alternatives --config python3
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.9 get-pip.py
    ```

4. git の設定
    ```
    git config --global user.name "Gitに登録しているユーザ名"
    git config --global user.email Gitに登録しているメアド
    git config  --global core.autocrlf false
    git config  --global core.quotepath false
    git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/libexec/git-core/git-credential-manager-core.exe"
    ```

5. git clone
    ```
    git clone https://github.com/s-hata-z/presidentblog-bot_RAG.git
    ```

6. 仮想環境の構築
    ```
    cd ..
    python3.9 -m venv venv
    ```

7. 仮想環境の起動
    ```
    source venv/bin/activate
    cd presidentblog-bot_UI
    ```

8. requirements.txt からライブラリをインストール
    ```
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install flask faiss-cpu pandas matplotlib "langchain==0.1.20" "langchain-community==0.0.38" "langchain-core==0.1.52" "langchain-openai==0.1.7" "langchain-text-splitters==0.0.2"
    ```

### 2. RAG用Index作成（初回のみ）
1. ナレッジ元となるCSVファイルの用意<br>
    CSVファイルを以下に配置：db/knowledge_data.csv
2. コードの実行<br>
    RAG構築のVectorDBを作成するため、以下を実行して下さい。
    ```
    cd db
    python faiss_indexing.py
    cd ../
    ```

### 3. 画像準備（初回のみ）
bot側UIのアイコン画像、3Dモデル背景画像の設定を行います。

- bot側UIのアイコン画像
    - botの画像アイコンを以下に配置：static/images/bot-icon.png
    - userの画像アイコンを以下に配置：static/images/user-icon.png
- 3Dモデル背景画像
    - 背景画像を以下に配置：static/images/background.jpg

### 4. モデル/アニメーション準備
3Dモデル（VRMファイル）、アニメーション（VRMAファイル）の設定を行います。

- 3Dモデルを以下に配置：static/models/vrm/vrm_model.vrm
- アニメーションを以下に配置（計4つ）：static/motions/vrma/SampleN.vrma
- "/templates/index.html"の193行～197行の内容を配置したアニメーションファイルに更新して下さい。<br>

    例）Sample1,2,3,4を配置した場合
    ```
    // アニメーション設定
    const Starting_vrma = '/static/motions/vrma/Sample1.vrma'   //起動時に再生するアニメーション
    const StanBy_vrma = '/static/motions/vrma/Sample2.vrma'     //一定時間経過後、操作がない場合に再生するアニメーション
    const Thinking_vrma = '/static/motions/vrma/Sample3.vrma'   //回答準備中に再生するアニメーション
    const Answering_vrma = '/static/motions/vrma/Sample4.vrma'  //回答生成完了時に再生するアニメーション
    ```

### 5. 環境変数（毎回行うこと）
本アプリケーションを使うにあたり、各keyを認識させておいて下さい。
```
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="..."
export LLM_MODELS="..."
export LLM_MODELS_TURBO="..."
export EM_MODELS="..."
export FILE_PATH="/home/ubuntu/presidentblog-bot_RAG"
```

### 6.アプリの起動（毎回行うこと）
GitのソースをEC2に配置後、以下を実行して下さい。
```
cd ../
source venv/bin/activate
cd presidentblog-bot_RAG
python main.py
```

## オプション
### 1. ログイン画面の有無
main.pyにて、"ログイン画面を使いたい場合" の内容をアンコメントし、"ログイン画面を使わない場合" の内容をコメントアウトすると使えるようになります。
