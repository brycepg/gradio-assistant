import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_core.documents import Document
from langchain_chroma import Chroma

from gradio_assistant.discord_qa_embeddings import COLLECTION_NAME, embeddings, CHUNK_OVERLAP, CHUNK_SIZE

PERSIST_DIRECTORY="chroma_db"
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)


def list_all_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def main():
    file_seq = list_all_files("data/gradio-questions")
    documents = []
    for file in file_seq:
        with open(file, 'r', encoding="utf-8") as fh:
            document_text = fh.read()
        documents.extend(
            [Document(page_content=x) for x in text_splitter.split_text(document_text)]
        )

    print(len(documents))

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME,
    )


if __name__ == "__main__":
    main()
