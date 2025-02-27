import json

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from gradio_assistant.url_result import UrlResult
from gradio_assistant.docs_embeddings import COLLECTION_NAME, embeddings, CHUNK_OVERLAP, CHUNK_SIZE

def url_result_to_documents(url_result: UrlResult):
    metadata = {"source": url_result.url}
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs = [Document(page_content=x, metadata=metadata) for x in text_splitter.split_text(url_result.content)]
    return docs

def main():
    with open("data/gradio-docs-text.json") as fh:
        json_seq = json.load(fh)
    url_results = [UrlResult(**x) for x in json_seq]
    documents = []
    for url_result in url_results:
        documents.extend(url_result_to_documents(url_result))

    print(len(documents))

    persist_directory = "chroma_db"

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=COLLECTION_NAME,
    )

if __name__ == "__main__":
    main()
