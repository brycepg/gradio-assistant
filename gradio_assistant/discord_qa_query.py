from langchain_chroma import Chroma
from gradio_assistant.discord_qa_embeddings import COLLECTION_NAME, embeddings

persist_directory = "chroma_db"

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=persist_directory,
)

async def query_discord_qa(query):
    """Search gradio Q&A site in a vector database and return relevant information

    Args:
        query (str): The user query
    """
    print(f"Query: {query}")
    vector_documents = await vector_store.asimilarity_search_with_score(query, k=3)
    results = []
    for res, score in vector_documents:
        results.append([res.page_content])
        print("----------------------------------------------------")
        print(f"* {res.page_content}: score={score}")
    return results
