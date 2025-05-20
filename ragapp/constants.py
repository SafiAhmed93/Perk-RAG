from langchain_community.vectorstores.azuresearch import AzureSearch
from azure.identity import (
    DefaultAzureCredential,
)
from langchain_community.retrievers import AzureAISearchRetriever
import json
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from typing import List, Dict
from ragapp.models.models import SearchResult

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


data_store = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_AI_SEARCH_API_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    embedding_function=embedder.embed_query,
    azure_credential=api_key,
    vector_search=True,
)


def query_search(
    query: str,
    index_name: str = os.getenv("AZURE_SEARCH_INDEX_NAME"),
    endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT"),
    top_k: int = 3,
):

    if index_name is None or endpoint is None:
        raise ValueError("Index name or endpoint is not set in environment variables.")

    search_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")),
    )

    vector_query = VectorizableTextQuery(
        text=query, k_nearest_neighbors=10, fields="content_vector"
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        top=top_k,
    )
    data = []

    for result in results:
        search = {}

        search["doc_name"] = (
            json.loads(result.get("metadata")).get("source").split("/")[-1]
        )
        search["content"] = result.get("content")

        data.append(search)
    return data


llm = AzureChatOpenAI(
    api_key=api_key,
    azure_deployment="gpt-4o-mini",
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPEN_AI_ENDPOINT"),
)

SYSTEM_MESSAGE = """
    You are a helpful agent. You're job is to read the context provided below and then answer the questions from it.
    Format the answer so it is easily readable, and make it as concise as possible. Remove the slash n char and any other extraneous characters.
    Make sure the answers are easily understandable and clear. 
    """

REWRITE_QUERY_SYSTEM_MESSAGE = """

        You are a smart assistant. Based on the conversation below, resolve the user's latest question by replacing any 
        pronouns or references with actual entities.
        """
