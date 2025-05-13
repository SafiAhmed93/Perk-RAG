from json import load
from langchain_community.vectorstores.azuresearch import AzureSearch
from azure.identity import (
    DefaultAzureCredential,
)
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
import os
from langchain_openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=500)

api_key = (
    DefaultAzureCredential().get_token("https://cognitiveservices.azure.com")
).token

embedder = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-ada-002",
    azure_endpoint="https://brio-calliq-poc.openai.azure.com/",
    model="text-embedding-ada-002",
    api_key=api_key,
    api_version="2023-05-15",
)

print(os.getenv("AZURE_SEARCH_ENDPOINT"))

data_store = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    embedding_function=embedder.embed_query,
    azure_credential=api_key,
)

llm = AzureChatOpenAI(
    api_key=api_key,
    azure_deployment="gpt-4o-mini",
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPEN_AI_ENDPOINT"),
)

SYSTEM_MESSAGE = """
    You are a helpful agent. You're job is to read the context provided below and then answer the questions from it.
    Format the answer so it is easily readable, and make it as concise as possible.
    """
