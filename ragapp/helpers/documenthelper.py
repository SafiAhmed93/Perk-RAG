from ragapp.models.models import Document
from ragapp.prepdocslib.blobhelper2 import BlobHelper
from langchain_core.document_loaders import BaseLoader
from langchain_text_splitters.base import TextSplitter
from langchain_core.documents import Document as Langchain_Document
from langchain_core.vectorstores import VectorStore


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

    def query(self, user_query: str):
        return self.data_store.similarity_search_with_relevance_scores(
            query=user_query, k=1, score_threshold=0.8
        )

    def process(self):
        # try:
        content = self.get_content()
        docs = self.split(content)
        self.embed_and_save(docs)
        return 0
        # except Exception as e:
        #     return 1
