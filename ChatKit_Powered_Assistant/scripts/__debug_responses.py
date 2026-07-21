import os, asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url=os.getenv('OPENAI_BASE_URL'),
    api_key=os.getenv('OPENAI_API_KEY'),
)


async def main():
    stream = await client.responses.create(
        model='agnes-2.0-flash',
        input=[{'role': 'user', 'content': 'Say hi in Chinese in 5 words.'}],
        stream=True,
    )
    text = ''
    async for chunk in stream:
        delta = getattr(chunk, 'delta', None)
        if delta and getattr(delta, 'text', None):
            text += delta.text
    print('TEXT', text.strip() or '<empty>')


asyncio.run(main())