import asyncio

from gradio_assistant.discord_qa_query import query_discord_qa

async def main():
    results = await query_discord_qa("Deactivate the retry and undo features in Chatbot")
    # results = await query_discord_qa("test")
    # for result in results:
    #     print("----------------------------------------------------")
    #     print(result)

if __name__ == "__main__":
    asyncio.run(main())
