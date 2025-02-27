from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)
COLLECTION_PREFIX = "gradio-docs"
EMBEDDING_POSTFIX = "openai-large"
CHUNK_OVERLAP = 128
CHUNK_SIZE = 2048
COLLECTION_NAME = f"{COLLECTION_PREFIX}-{CHUNK_SIZE}-{CHUNK_OVERLAP}-{EMBEDDING_POSTFIX}"
