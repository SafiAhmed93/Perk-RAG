from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceExistsError
from pdfparse import PdfParse
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class EmbeddingSearchManager:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.api_key = self.credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token
        self.parser = PdfParse()
        os.environ["OPENAI_API_TYPE"] = "azure_ad"

    # @staticmethod
    def create_embeddings(self) -> AzureOpenAIEmbeddings:

        logger.info("Creating embeddings")

        return AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPEN_AI_EMBEDDING_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPEN_AI_ENDPOINT"),
            api_key=self.api_key,
        )

    def azure_search(self) -> AzureSearch:

        try:
            logger.info("Creating the Index")
            return AzureSearch(
                azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
                azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
                index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
                embedding_function=self.create_embeddings().embed_query,
            )
        except ResourceExistsError:
            logger.info("Index already exists, moving on")

    def load_split_insert(self, file_name: str) -> list[str]:
        """
        Loads a PDF document from Azure storage into Langchain document object, Splits the the document into chunks, embeds the data
        and stores them in the index.
        """
        documents = self.parser.get_page_content(file_name)
        logger.info("Documents retrieved")
        text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=500)
        docs = text_splitter.split_documents(documents)
        logger.info("Documents split into chunks")
        logger.info("Done with the prep")

        return self.azure_search().add_documents(docs)

    def query_vector_db(self, query: str):
        return self.azure_search().similarity_search_with_relevance_scores(
            query, k=4, score_threshold=0.8
        )
