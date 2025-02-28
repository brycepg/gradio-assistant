import asyncio

from gradio_assistant.github_query import query_github_issues

async def main():
    results = await query_github_issues("Maintain session state with ChatInterface?")
    # results = await query_stackoverflow("remove the tagline")
    # results = await query_discord_qa("test")
    # for result in results:
    #     print("----------------------------------------------------")
    #     print(result)

if __name__ == "__main__":
    asyncio.run(main())
