from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from ragapp.constants import llm, data_store, api_key


load_dotenv()


chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@chat_router.get("/")
def get_chat():
    return "chat"


@chat_router.post("/")
def get_results(user_query: str):

    SYSTEM_MESSAGE = """
        You are a helpful agent. You're job is to read the context provided below and then answer the questions from it.
        Format the answer so it is easily readable, and make it as concise as possible.
        """

    raw_context = data_store.similarity_search_with_relevance_scores(
        query=user_query, k=3, score_threshold=0.8
    )

    context = "/n".join([content[0].page_content for content in raw_context])

    response = llm.invoke(f"{SYSTEM_MESSAGE} \n {context} \n {user_query}")
    return response.content
