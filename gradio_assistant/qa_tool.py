import asyncio

from gradio_assistant.discord_qa_query import query_discord_qa
from gradio_assistant.stackoverflow_query import query_stackoverflow
from gradio_assistant.github_query import query_github_issues

async def qa_query(query: str):
    """Search Q&A site in a vector database and return relevant information

    Args:
        query (str): The user query
    """
    print(f"Query: {query}")
    discord_resuts, stackoverflow_results, github_results = asyncio.gather(
        query_discord_qa(query),
        query_stackoverflow(query),
        query_github_issues(query),
    )
    return [
        *discord_resuts,
        *stackoverflow_results,
        *github_results,
    ]
