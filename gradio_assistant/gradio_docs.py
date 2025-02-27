from langchain_chroma import Chroma
from gradio_assistant.docs_embeddings import COLLECTION_NAME, embeddings

persist_directory = "chroma_db"

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=persist_directory,  # Where to save data locally, remove if not necessary
)

async def query_documents(query):
    """Search gradio documents and guides in a vector database and return relevant information

    Args:
        query (str): The user query
    """
    print(f"Query: {query}")
    vector_documents = await vector_store.asimilarity_search_with_score(query, k=3)
    results = []
    for res, score in vector_documents:
        results.append({
            "content": res.page_content,
            "url": res.metadata["source"],
        })
        print("----------------------------------------------------")
        print(f"* {res.page_content} [{res.metadata}]: score={score}")
    return results
