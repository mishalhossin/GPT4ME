import re
import json
import base64
import random
import string
import aiohttp
import asyncio
from fake_useragent import UserAgent

class ChatCompletion:
    @staticmethod
    async def create(
            messages: list,
            context: str = "Converse as if you were an AI assistant. Be friendly, creative.",
            restNonce: str = None,
            proxy: str = None
    ):
        url = "https://chatgptlogin.ac/wp-json/ai-chatbot/v1/chat"
        if not restNonce:
            restNonce = await ChatCompletion.get_restNonce(proxy)
        headers = {
            "Content-Type": "application/json",
            "X-Wp-Nonce": restNonce
        }
        proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy} if proxy else None
        data = {
            "env": "chatbot",
            "session": "N/A",
            "prompt": ChatCompletion.__build_prompt(context, messages),
            "context": context,
            "messages": messages,
            "newMessage": messages[-1]["content"],
            "userName": "<div class=\"mwai-name-text\">User:</div>",
            "aiName": "<div class=\"mwai-name-text\">AI:</div>",
            "model": "gpt-3.5-turbo",
            "temperature": 0.8,
            "maxTokens": 1024,
            "maxResults": 1,
            "apiKey": "",
            "service": "openai",
            "embeddingsIndex": "",
            "stop": "",
            "clientId": ChatCompletion.randomStr(),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=json.dumps(data), headers=headers, proxies=proxies) as response:
                if response.status == 200:
                    return await response.json()
                return await response.text()

    @staticmethod
    def randomStr():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=34))[:11]

    @classmethod
    def __build_prompt(cls, context: str, message: list, isCasuallyFineTuned=False, last=15):
        prompt = context + '\n\n' if context else ''
        message = message[-last:]
        if isCasuallyFineTuned:
            lastLine = message[-1]
            prompt = lastLine.content + ""
            return prompt
        conversation = [x["who"] + x["content"] for x in message]
        prompt += '\n'.join(conversation)
        prompt += '\n' + "AI: "
        return prompt

    @classmethod
    async def get_restNonce(cls, proxy: str = None):
        url = "https://chatgptlogin.ac/"
        headers = {
            "Referer": "https://chatgptlogin.ac/",
            "User-Agent": UserAgent().random
        }
        proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy} if proxy else None
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, proxies=proxies) as response:
                text = await response.text()
                src = re.search(
                    'class="mwai-chat mwai-chatgpt">.*<span>Send</span></button></div></div></div> <script defer src="(.*?)">',
                    text).group(1)
                decoded_string = base64.b64decode(src.split(",")[-1]).decode('utf-8')
                restNonce = re.search(r"let restNonce = '(.*?)';", decoded_string).group(1)
                return restNonce

class Completion:
    @staticmethod
    async def create(prompt: str, proxy: str):
        messages = [
            {
                "content": prompt,
                "html": prompt,
                "id": ChatCompletion.randomStr(),
                "role": "user",
                "who": "User: ",
            },
        ]
        return await ChatCompletion.create(messages=messages, proxy=proxy)
