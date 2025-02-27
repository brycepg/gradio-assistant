import asyncio

from gradio_assistant.gradio_docs import query_documents

SCORE_THRESHOLD = 1.2

async def main():
    results = await query_documents("How do I create a multi-page app?")
    # for result in results:
    #     print("----------------------------------------------------")
    #     print(result)

if __name__ == "__main__":
    asyncio.run(main())
