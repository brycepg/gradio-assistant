results = vector_store.similarity_search(
    query,
    k=2,
    # filter={"source": "tweet"}
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")
