import logging

from langchain_chroma import Chroma
from gradio_assistant.github_embeddings import COLLECTION_NAME, embeddings

persist_directory = "chroma_db"

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=persist_directory,
)

logger = logging.getLogger(__name__)

async def query_github_issues(query):
    """Search github issues in a vector database and return relevant information

    Args:
        query (str): The user query
    """
    vector_documents = await vector_store.asimilarity_search_with_score(query, k=3)
    results = []
    for res, score in vector_documents:
        results.append({
            "content": res.page_content,
            "url": res.metadata["source"],
        })
        logging.info("---------------------github-------------------------")
        logging.info(f"* {res.page_content} [{res.metadata}]: score={score}")
        logging.info("----------------------end github--------------------")
    return results
