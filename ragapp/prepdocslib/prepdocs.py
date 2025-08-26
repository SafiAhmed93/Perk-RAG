from embeddingsearchmanager import EmbeddingSearchManager
import logging

# from rich.logging import RichHandler

# logging.basicConfig(
#     format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
# )
# We only set the level to INFO for our logger,
# to avoid seeing the noisy INFO level logs from the Azure SDKs
# logger.setLevel(logging.INFO)

manager = EmbeddingSearchManager()

vectore_store = manager.azure_search()

insert_into_index = manager.load_split_insert("complaints-commitee.pdf")

answer = manager.query_vector_db(
    "Who is the presiding officer for internal complaints commitee?, give his contact information"
)

print(answer)
