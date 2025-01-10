# VsCode + Python によるセットアップ

社長botのセットアップにて、ローカル環境のVSCodeを用いる場合の対応を以下に記載します。

### 0. 各ツールのインストール（初回のみ）
- VSCodeを以下のURLからダウンロード<br>
  - *https://code.visualstudio.com/*

- PythonをMicrosoftからダウンロード<br>
  - *https://apps.microsoft.com/detail/9p7qfqmjrfp7?hl=ja-JP&gl=JP*

### 1. 当リポジトリからコードの入手
以下のURLをクリックして、コードをローカルにダウンロード<br>
  - *https://github.com/SakutoHata/president-bot_RAG/archive/refs/heads/main.zip*

### 2. VSCodeの準備（初回のみ）
VSCodeを立ち上げた後、以下の対応を行います。
#### 2-1. 拡張機能の追加
以下のURL先からVSCodeに拡張機能を追加します。<br>
- *https://marketplace.visualstudio.com/items?itemName=ms-python.python*

- *https://marketplace.visualstudio.com/items?itemName=MS-CEINTL.vscode-language-pack-ja*

#### 2-2. Pythonの設定
VSCode上部の「表示＞コマンドパレット＞Python: インタープリターを選択」をクリックする。<br>
その後、以下のような画面が表示されるため、インストールしたPythonのバージョン（3.9.X）を選択して下さい。

#### 2-3. ライブラリのインストール
以下のコードを実行する。
  ```
  pip install -r requirements.txt
  pip install flask faiss-cpu pandas matplotlib "langchain==0.1.20" "langchain-community==0.0.38" "langchain-core==0.1.52" "langchain-openai==0.1.7" "langchain-text-splitters==0.0.2"
  ```

#### 2-4. 環境変数の設定
本アプリケーションを使うにあたり、"*presidentblog-bot_RAG/.env*" にて、各keyを認識させておいて下さい。
```
AZURE_OPENAI_API_KEY="..."      # AzureOpenAI のkey
AZURE_OPENAI_ENDPOINT="..."     # AzureOpenAI の エンドポイント
LLM_MODELS="..."                # 対話用 model のkey
EM_MODELS="..."                 # embedding model のkey
FILE_PATH="..."                 # presidentblog-bot_RAG/srcの配置
MODE="csv_index"
```

#### 2-5. 各ファイルの配置

- *CSVファイルの配置*<br>
  "*src/db/csv_index/add_data*"にベクトルDBの際参照する、CSVファイルを配置

- *アイコン画像の配置*<br>
  bot側UIのアイコン画像、3Dモデル背景画像の設定を行います。
  - *bot側UIのアイコン画像*
      - botの画像アイコンを以下に配置：*src/static/images/bot-icon.png*
      - userの画像アイコンを以下に配置：*src/static/images/user-icon.png*
  - *3Dモデル背景画像*
      - 背景画像を以下に配置：*src/static/images/background.jpg*

- *モデル/アニメーション準備*<br>
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

### 3. アプリケーションの起動
　"*src/main.py*" を実行し、ブラウザを立ち上げる。<br>立ち上げた後、ローカルホストにアクセスすることで利用できるようになる。