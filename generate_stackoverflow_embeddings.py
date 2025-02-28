import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from markdownify import markdownify as md

from gradio_assistant.utils import list_all_files
from gradio_assistant.stackoverflow_embeddings import COLLECTION_NAME, embeddings, CHUNK_OVERLAP, CHUNK_SIZE
from gradio_assistant.url_result import UrlResult

PERSIST_DIRECTORY = "chroma_db"
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
directory = "data/stackoverflow"


def url_result_to_documents(url_result: UrlResult):
    metadata = {"source": url_result.url}
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs = [Document(page_content=x, metadata=metadata) for x in text_splitter.split_text(url_result.content)]
    return docs


def main():
    file_seq = list_all_files(directory)
    qa_seq = []
    for file in file_seq:
        with open(file, 'r', encoding="utf-8") as fh:
            qa_seq.extend(json.load(fh))

    print(file_seq)
    print(len(qa_seq))
    question_id_seq = set()
    qa_filtered = []
    for qa in qa_seq:
        if not qa["answers"]:
            continue
        question_id = qa["question_id"]
        if question_id in question_id_seq:
            continue
        qa_filtered.append(qa)
        question_id_seq.add(question_id)
    print(len(qa_filtered))

    url_result_seq = []
    for qa in qa_filtered:
        answers_body = "\n\n".join([md(x["body"]) for x in qa["answers"]])
        url_result_seq.append(
            UrlResult(
                content="#" + qa["title"] + "\n\n" + md(qa["body"]) + answers_body,
                url=qa["link"],
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
