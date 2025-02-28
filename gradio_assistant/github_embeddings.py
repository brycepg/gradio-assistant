from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import SentenceTransformerEmbeddings

CHUNK_SIZE = 2048
CHUNK_OVERLAP = 0
COLLECTION_PREFIX = "github-issues-3"
# EMBEDDING_POSTFIX = "minilm"
# embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
EMBEDDING_POSTFIX = "openai-large"
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)
COLLECTION_NAME = f"{COLLECTION_PREFIX}-{CHUNK_SIZE}-{CHUNK_OVERLAP}-{EMBEDDING_POSTFIX}"
