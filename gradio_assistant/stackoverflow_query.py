import logging

from langchain_chroma import Chroma
from gradio_assistant.stackoverflow_embeddings import COLLECTION_NAME, embeddings

persist_directory = "chroma_db"

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=persist_directory,
)

logger = logging.getLogger(__name__)

async def query_stackoverflow(query):
    """Search StackOverflow in a vector database and return relevant information

    Args:
        query (str): The user query
    """
    vector_documents = await vector_store.asimilarity_search_with_score(query, k=2)
    results = []
    for res, score in vector_documents:
        results.append({
            "content": res.page_content,
            "url": res.metadata["source"],
        })
        logger.info("-----------------stackoverflow----------------------")
        logger.info(f"* {res.page_content} [{res.metadata}]: score={score}")
        logger.info("-----------------staendverflow----------------------")
    return results
