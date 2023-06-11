import aiohttp
import asyncio
import json

async def generate_response(messages):
    url = "https://askgpt.cn/api/openai/v1/chat/completions"
    headers = {
        "accept": "text/event-stream",
        "content-type": "application/json",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    data = {
        "messages": messages,
        "stream": True,
        "model": "gpt-3.5-turbo",
        "temperature": 0.5,
        "presence_penalty": 0
    }

    combined_response = ""  # Variable to accumulate the responses

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as response:
            async for line in response.content:
                chunk = line.decode().strip()
                if chunk == "data: [DONE]":
                    break
                if chunk.startswith("data:"):
                    chunk_data = json.loads(chunk.replace("data: ", ""))
                    if "choices" in chunk_data:
                        choices = chunk_data["choices"]
                        for choice in choices:
                            delta = choice["delta"]
                            content = delta.get("content")
                            if content is not None:
                                combined_response += content

    print(f"Response: {combined_response}")

async def main():
    await generate_response()

asyncio.run(main())
