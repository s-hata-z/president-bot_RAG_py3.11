import pandas as pd
import os
import re
from langchain.vectorstores import FAISS  # ベクトル検索（近傍探査）
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings # AzureOpenAIEmbeddings 追加
from langchain_community.document_loaders.csv_loader import CSVLoader

FILE_PATH = os.environ["FILE_PATH"]
file_path = f"{FILE_PATH}/db/knowledge_data.csv"
blog_data = pd.read_csv(file_path)

AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
LLM_MODELS_TURBO = os.environ["LLM_MODELS_TURBO"]
EM_MODELS = os.environ["EM_MODELS"]

llm = AzureChatOpenAI(openai_api_version="2024-08-01-preview",
                      azure_endpoint=AZURE_OPENAI_ENDPOINT,
                      openai_api_type="azure",
                      openai_api_key=AZURE_OPENAI_API_KEY,
                      deployment_name=LLM_MODELS_TURBO,
                      temperature=0)


embedding = AzureOpenAIEmbeddings(openai_api_version="2024-08-01-preview",
                                  azure_endpoint=AZURE_OPENAI_ENDPOINT,
                                  openai_api_type="azure",
                                  openai_api_key=AZURE_OPENAI_API_KEY,
                                  model=EM_MODELS)

# knowledge chunking
def chunking_data(file_path):
        loader = CSVLoader(file_path, autodetect_encoding=True)
        documents = loader.load()

        for doc in documents:
            cleaned_content = doc.page_content.replace("\n", "").replace("\u3000", "").replace("   ", "")
            cleaned_content = re.sub(r"^\d+\s", "", cleaned_content)
            doc.page_content = cleaned_content

        knowledge = documents

        file = open(f"{FILE_PATH}/db/knowledge_logs.txt", mode='w', encoding='utf-8')
        file.write(str(knowledge))
        file.close()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=100,
        )

        splitted_documents = text_splitter.split_documents(knowledge)

        return splitted_documents
    
    
splitted_documents = chunking_data(file_path)
vector_store = FAISS.from_documents(documents=splitted_documents, embedding=embedding)
vector_store.save_local(f"{FILE_PATH}/db")
