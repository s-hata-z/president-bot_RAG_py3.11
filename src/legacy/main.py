import os
import json
import re
import logging
import secrets  # secretsモジュールをインポート
from flask import Flask, Response, request, render_template, stream_with_context, abort, jsonify, redirect, url_for, flash, session
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores.faiss import FAISS
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def check_file_exists(file_path):
    return os.path.isfile(f"{FILE_PATH}/{file_path}")

# Environment variables
FILE_PATH = os.environ["FILE_PATH"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
LLM_MODELS = os.environ["LLM_MODELS"]
EM_MODELS = os.environ["EM_MODELS"]


# Initialize AzureChatOpenAI LLM with streaming enabled
llm = AzureChatOpenAI(
    openai_api_version="2024-08-01-preview", #"2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    openai_api_type="azure",
    openai_api_key=AZURE_OPENAI_API_KEY,
    deployment_name=LLM_MODELS,
    temperature=0,
    streaming=True  # Enable streaming
)

# Initialize generation model
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-08-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

# Initialize embedding model
embedding = AzureOpenAIEmbeddings(
    openai_api_version="2023-05-15",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    openai_api_type="azure",
    openai_api_key=AZURE_OPENAI_API_KEY,
    model=EM_MODELS,
)

app = Flask(__name__)

# セッション情報
app.secret_key = secrets.token_hex(16)  # 16バイト（32文字）のランダムなシークレットキーを生成

# ログの設定
logging.basicConfig(level=logging.INFO)  # ログレベルをINFOに設定

# FAISS vector storeの読み込み
vector_store = FAISS.load_local(f"{FILE_PATH}/db", embeddings=embedding, allow_dangerous_deserialization=True)

# retrieverの作成
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Prompt設定

## botのキャラクター性に関するもの
# 使用例
character_prompt_file_path = 'prompts/character_prompts.txt'
if check_file_exists(character_prompt_file_path):
    print("character_prompts ファイルが存在します")
    with open(f'{FILE_PATH}/prompts/character_prompts.txt', 'r', encoding='utf-8') as f:
        character_prompt = f.read()
else:
    print("character_prompts ファイルが存在しません")
    with open(f'{FILE_PATH}/prompts/character_prompts_Sample.txt', 'r', encoding='utf-8') as f:
        character_prompt = f.read()

## systemの設定
sys_prompt_file_path = 'prompts/system_prompts.txt'
if check_file_exists(sys_prompt_file_path):
    print("system_prompts ファイルが存在します")
    with open(f'{FILE_PATH}/prompts/system_prompts.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
else:
    print("system_prompts ファイルが存在しません")
    with open(f'{FILE_PATH}/prompts/system_prompts_Sample.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read()

response_data = []

@app.before_request
def before_request():
    if request.headers.get('X-Forwarded-Proto') == 'https':
        request.environ['wsgi.url_scheme'] = 'https'

@app.route('/health')
def health():
    return 'Healthy', 200

## ログイン画面を使いたい場合
## ユーザー情報（例: デモ用にユーザー名とパスワードを固定）
# USERNAME = os.environ["USERNAME"]
# PASSWORD = os.environ["PASSWORD"]

# @app.route('/')
# def index():
#     # ログインしていない場合はログインページにリダイレクト
#     if not session.get("logged_in"):
#         return redirect(url_for("login"))
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         # 認証チェック
#         if not username:
#             flash("ユーザー名を入力してください", "error")
#         elif not password:
#             flash("パスワードを入力してください", "error")
#         elif username != USERNAME or password != PASSWORD:
#             flash("ユーザー名またはパスワードが正しくありません", "error")
#         else:
#             session["logged_in"] = True
#             flash("ログインに成功しました！", "success")
#             return redirect(url_for("index"))
        
#     return render_template("login.html")

# ログイン画面を使わない場合
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat(system_prompt = system_prompt):
    user_message = request.json['message']
    retrieved_docs = retriever.invoke(user_message)
    contents = [re.search(r"Contents:\s*(.*)", doc.page_content).group(1) for doc in retrieved_docs if re.search(r"Contents:\s*(.*)", doc.page_content)]
    print("\n",contents)
    contents_str = "[\n" + ",\n".join(contents) + "\n]"
    print(type(contents_str))
    system_prompt = system_prompt.replace("nearly_contens", contents_str)
    def generate():
        stream = client.chat.completions.create(
            model="kuralab_eastus2_gpt-4o",
            messages=[{"role": "system", "content": character_prompt},{"role": "system", "content": system_prompt},*response_data,{"role": "user", "content": user_message}],
            stream=True
        )
        print("\n", system_prompt)
        answer_data = {"role": "assistant", "content": "answer"}
        answers = ""
        for chunk in stream:
            #print(chunk)
            if chunk.choices and chunk.choices[0].delta.content is not None:
                answers += chunk.choices[0].delta.content.encode('utf-8').decode('utf-8')
                yield chunk.choices[0].delta.content.encode('utf-8')
        answer_data["content"] = answers
        print("\n",answer_data)
        user_message_data = {"role": "user", "content": user_message}
        system_message_data = {"role": "system", "content": f"以下を参照して回答しなさい。\n {contents_str}"}
        response_data.append(user_message_data)
        response_data.append(system_message_data)
        response_data.append(answer_data)
        if len(response_data) > 15:
            del response_data[:3]  # 最初の2つの要素を削除
        print("\n",response_data)
        
    return Response(stream_with_context(generate()), content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)