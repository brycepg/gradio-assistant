import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from markdownify import markdownify as md

from gradio_assistant.utils import list_all_files
from gradio_assistant.github_embeddings import COLLECTION_NAME, embeddings, CHUNK_OVERLAP, CHUNK_SIZE
from gradio_assistant.url_result import UrlResult

PERSIST_DIRECTORY = "chroma_db"
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
file_path = "./data/github-issues-filtered.json"


def url_result_to_documents(url_result: UrlResult):
    metadata = {"source": url_result.url}
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs = [Document(page_content=x, metadata=metadata) for x in text_splitter.split_text(url_result.content)]
    return docs


def main():
    with open(file_path, 'r', encoding="utf-8") as fh:
        json_document = json.load(fh)

    print(len(json_document))
    url_result_seq = []
    for url_result_json in json_document:
        url_result_seq.append(
            UrlResult(
                **url_result_json
            )
        )
    documents = []
    for url_result in url_result_seq:
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
