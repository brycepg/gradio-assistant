from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import SentenceTransformerEmbeddings

CHUNK_SIZE = 2048
CHUNK_OVERLAP = 0
COLLECTION_PREFIX = "stakoverflow-qa-2"
# EMBEDDING_POSTFIX = "minilm"
EMBEDDING_POSTFIX = "openai-large"
# embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)
COLLECTION_NAME = f"{COLLECTION_PREFIX}-{CHUNK_SIZE}-{CHUNK_OVERLAP}-{EMBEDDING_POSTFIX}"
