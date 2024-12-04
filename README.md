# 社長ボット

## はじめに
インターンでPoCのため、作成いたしました。<br>
3Dモデルとコミュニケーション可能かつ、RAG構成のフロントおよびバックエンドを構築したWebアプリです。当リポジトリではアプリのみの解説を行っております。

## プロジェクト開始時点の要求
- Microsoft Teamsで動作可能なこと
- Webアプリの構築も同時に行ってほしい
- 対話しているように感じることのできるUIにしてほしい（VRみたいな感じ）
- 性能のよい生成AIを使いたい（当時ではOpenAI系モデルがトップだった...）
- AWSとAzureOpenAIを組み合わせることができるか検証してほしい
- 社長が執筆した文書をナレッジとしたチャットボットが欲しい（CSVデータ）

## システム構成
#### Teams対応版
![ボット構成図](/images/ボット構成図.png)<br>
基本的に、AzureOpenAIとAWSのEC2を接続する構成となっています。<br>
AWS Certificate Managerでドメインを取得し、ALBにアタッチする形でレコードを作成することで、WAFを通じてアクセス可能なデバイス側のIPアドレスを制限しました。

## セットアップ
「*初回のみ*」と付くものは、初回で必須の対応となります。<br>
初回以降は、「[3.環境変数](#3-環境変数毎回行うこと)」、「[7.アプリの起動](#7アプリの起動毎回行うこと)」の順で実行して下さい。

※アプリの動作検証のみをしたい方は、「[2. 他環境にてセットアップ](#2-他環境にてセットアップ)」を参考にして下さい。

### 1. EC2の設定（初回のみ）
- アプリケーションおよびOSイメージ：*Ubuntu*
- インスタンスタイプ：*t2.small*
- セキュリティグループ：Azure側（OpenAIのエンドポイント）、VSCode側（Flask）と通信可能にしておく
- キーペア：新規作成して下さい。ここで生成されたkeyファイルは開発用PCの".sshフォルダ"に格納し、VSCodeのリモート開発機能等を使って当リポジトリを導入してください。

※ElasticIPの割り当て、ドメイン発行、WAFの適応はここでは紹介しないが行っておくこと。

### 2. VSCode環境構築（初回のみ）
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
    git clone https://github.com/SakutoHata/president-bot_RAG.git
    ```

6. 仮想環境の構築
    ```
    cd ..
    python3.9 -m venv venv
    ```

7. 仮想環境の起動
    ```
    source venv/bin/activate
    cd presidentblog-bot_RAG
    ```

8. requirements.txt からライブラリをインストール
    ```
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install flask faiss-cpu pandas matplotlib "langchain==0.1.20" "langchain-community==0.0.38" "langchain-core==0.1.52" "langchain-openai==0.1.7" "langchain-text-splitters==0.0.2"
    ```

### 3. 環境変数（毎回行うこと）
本アプリケーションを使うにあたり、"*presidentblog-bot_RAG/.env*" にて、各keyを認識させておいて下さい。
```
AZURE_OPENAI_API_KEY="..."      # AzureOpenAI のkey
AZURE_OPENAI_ENDPOINT="..."     # AzureOpenAI の エンドポイント
LLM_MODELS="..."                # 対話用 model のkey
LLM_MODELS_TURBO="..."          # embedding model のkey
EM_MODELS="..."                 # embedding model のkey
FILE_PATH="..."                 # presidentblog-bot_RAG/srcの配置
```

### 4. RAG用Index作成（初回のみ）
1. ナレッジ元となるCSVファイルの用意<br>
    CSVファイルを以下に配置：*src/db/knowledge_data.csv*
2. コードの実行<br>
    RAG構築のVectorDBを作成するため、以下を実行して下さい。
    ```
    cd src/db
    python faiss_indexing.py
    cd ../
    ```

### 5. 画像準備（初回のみ）
bot側UIのアイコン画像、3Dモデル背景画像の設定を行います。

- bot側UIのアイコン画像
    - botの画像アイコンを以下に配置：*src/static/images/bot-icon.png*
    - userの画像アイコンを以下に配置：*src/static/images/user-icon.png*
- 3Dモデル背景画像
    - 背景画像を以下に配置：*src/static/images/background.jpg*

### 6. モデル/アニメーション準備（初回のみ）
3Dモデル（VRMファイル）、アニメーション（VRMAファイル）の設定を行います。

- 3Dモデルを以下に配置：*src/static/models/vrm/vrm_model.vrm*
- アニメーションを以下に配置（計4つ）：*src/static/motions/vrma/SampleN.vrma*
- "/templates/index.html"の193行～197行の内容を配置したアニメーションファイルに更新して下さい。<br>

    例）Sample1,2,3,4を配置した場合
    ```
    // アニメーション設定
    const Starting_vrma = '/static/motions/vrma/Sample1.vrma'   //起動時に再生するアニメーション
    const StanBy_vrma = '/static/motions/vrma/Sample2.vrma'     //一定時間経過後、操作がない場合に再生するアニメーション
    const Thinking_vrma = '/static/motions/vrma/Sample3.vrma'   //回答準備中に再生するアニメーション
    const Answering_vrma = '/static/motions/vrma/Sample4.vrma'  //回答生成完了時に再生するアニメーション
    ```

### 7.アプリの起動（毎回行うこと）
GitのソースをEC2に配置後、以下を実行して下さい。
```
cd ../..
source venv/bin/activate
cd presidentblog-bot_RAG/src
python main.py
```

### 8. Teamsへのアプリ登録（初回のみ）
1. "*manifest/manifest.json*" の記載<br>
実際に配置されているファイルを参照し、コメントが付いている箇所を適宜修正して下さい。

2. "*manifest/main_icon.png*"の用意<br>
ピクセルが"192×192"のサイズの画像を準備して下さい。

3. "*manifest/rest_icon.png*"の用意<br>
ピクセルが"32×32"のサイズの白黒透過画像を準備して下さい。

4. Developer PortalにUpload<br>
各ファイルをmanifestフォルダに格納後、zip化して下さい。<br>
そのzipファイルをmicrosoftの"[*Developer Portal*](https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=e1979c22-8b73-4aed-a4da-572cc4d0b832&scope=https%3A%2F%2Fdev.teams.microsoft.com%2FAppDefinitions.ReadWrite%20https%3A%2F%2Fdev.teams.microsoft.com%2FCards.ReadWrite%20openid%20profile%20offline_access&redirect_uri=https%3A%2F%2Fdev.teams.microsoft.com%2Fhome&client-request-id=a028b772-b5dc-4c5b-969a-e8c78f6abb9a&response_mode=fragment&response_type=code&x-client-SKU=msal.js.browser&x-client-VER=2.26.0&client_info=1&code_challenge=NKqjsSFzCj-FaEuscsP2g5iV_iaVOMxTewu3Y7wMZx4&code_challenge_method=S256&nonce=53f698a8-d0e7-488f-9532-785b159ae84c&state=eyJpZCI6IjU0OGY2YjdhLTcyMDEtNGNmNC04MThiLTYyNjBkMTRiMTAxNyIsIm1ldGEiOnsiaW50ZXJhY3Rpb25UeXBlIjoicmVkaXJlY3QifX0%3D)"にUploadすることで管理者から認証を得た場合にアプリの展開・利用が可能となります。<br>
また、microsoft Teamsの「*"アプリ" > "アプリを管理" > "アプリをアップロード"*」でzipファイルをUploadする方法でも同様のことが可能です。

## オプション
### 1. ログイン画面の有無
"*src/main.py*" にて、*"ログイン画面を使いたい場合"* の内容をアンコメントし、*"ログイン画面を使わない場合"* の内容をコメントアウトすると使えるようになります。

### 2. 他環境にてセットアップ
#### 2-1. EC2環境ではなくローカル環境で立ち上げる場合
Ubuntu環境を構築し、「[2-2.terminalで以下を実行](#2-vscode環境構築初回のみ)」→ 「[7.アプリの起動](#7アプリの起動毎回行うこと)」を行うことで、"localhost"扱いで立ち上げることが可能となる。この場合は、別途AzureのIP制限をデバイスのIPで既定する必要がある。

*なお、Ubuntu環境の構築については以下を例にセットアップして下さい。*
- 参考URL：https://qiita.com/zaburo/items/27b5b819fae2bde97a3b

#### 2-2. Docker環境で立ち上げる場合
この場合、"*requirements.txt*", 及び"*president-bot_RAG/.devcontainer*" を用いて、立ち上げてください。

なお、docker環境でアプリを動かす場合は、「[3. 環境変数](#3-環境変数毎回行うこと)」を必ず行うこと。

※以下は、Ubuntuからアプリを起動させる場合のコマンド
```
docker exec -it <コンテナ名> /bin/bash

cd ../app/repository/src

/usr/bin/python3 /app/repository/src/main.py
```

### 3. 3Dモデル / アニメーションの用意
今回採用した3DモデルはVRMファイル形式であるため、[*VRoidStudio*](https://vroid.com/studio)のようなツールで3Dモデルを作成する必要があります。（ fbxファイル形式などは[*UniVRM*](https://github.com/vrm-c/UniVRM)等を使ってVRMファイルに変換すればよい。詳しくは公式ドキュメントを参照して下さい。 ）<br>
また、VRMファイルにアニメーション適応するため、今回はVRMAファイルからアニメーションを取り込んでいます。アニメーションの作り方に疎い方は[*VRM Posing Desktop*](https://hub.vroid.com/apps/C5RyO1UeTrOT_gL5l4gXTgA_Lh819zgLdZmxhC-4kmw)(有料)などを使って作成して下さい。

### 4. チャットの回答文の設定
LangchainからPromptを取り込んでおります。チャットの回答文の語尾・語調、ロール等の設定はこちらで設定することで反映可能です。<br>
"*src/prompts/character_prompts_Sample.txt*" を参考に、同様の形式で"*src/prompts/character_prompts.txt*"を作成・配置して下さい。

### 5. RAGのSystem promptについて
こちらもLangchainからPromptを取り込んでおります。Agentic RAGとして機能させたい場合、外部検索処理を"src/main.py"に加え、その結果を変数として受け取れるようにする必要があります。<br>
"*src/prompts/system_prompts_Sample.txt*" を参考に、同様の形式で"*src/prompts/system_prompts.txt*"を作成・配置して下さい。
