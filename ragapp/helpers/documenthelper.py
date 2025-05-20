from ragapp.models.models import SearchResult
from ragapp.prepdocslib.blobhelper2 import BlobHelper
from langchain_core.document_loaders import BaseLoader
from langchain_text_splitters.base import TextSplitter
from langchain_core.documents import Document as Langchain_Document
from langchain_core.vectorstores import VectorStore
from langchain_community.retrievers import AzureAISearchRetriever
import os
from dotenv import load_dotenv
import json
from typing import List, Dict

load_dotenv()


class DocumentHelper:
    def __init__(
        self, splitter: TextSplitter, data_store: VectorStore, loader: BaseLoader = None
    ):
        self.splitter = splitter
        self.loader = loader
        self.data_store = data_store

    def get_content(self) -> list[Langchain_Document]:
        return self.loader.load()

    def split(
        self,
        content: list[Langchain_Document],
    ) -> list[Langchain_Document]:
        return self.splitter.split_documents(content)

    def embed_and_save(self, docs: list[Langchain_Document]) -> list[str]:
        return self.data_store.add_documents(docs)

    def query(self, user_query: str) -> List[SearchResult]:

        data = AzureAISearchRetriever(
            content_key="content",
            top_k=3,
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        ).invoke(user_query)

        search_results = []

        for doc in data:
            search_results.append(
                SearchResult(
                    doc_name=json.loads(doc.metadata.get("metadata"))
                    .get("source")
                    .split("/")[-1],
                    content=doc.page_content,
                )
            )

        return search_results

    def get_context(self, data: List[SearchResult]) -> str:

        return "\n".join([context.content for context in data])

    def get_docs(self, data: List[SearchResult]) -> List[str]:
        return list({context.doc_name for context in data})

    def process(self):
        try:
            content = self.get_content()
            docs = self.split(content)
            self.embed_and_save(docs)
            return 0
        except Exception as e:
            print(repr(e))
            return 1
