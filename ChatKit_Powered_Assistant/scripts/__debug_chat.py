import os, asyncio  
from openai import AsyncOpenAI  
base=os.getenv('OPENAI_BASE_URL','https://api.openai.com/v1')  
key=os.getenv('OPENAI_API_KEY')  
print('base',base)  
print('key_prefix', (key or '')[:12])  
client=AsyncOpenAI(base_url=base, api_key=key)  
async def go():  
    stream=await client.chat.completions.create(model='gpt-5-mini',messages=[{'role':'user','content':'hi'}],stream=True)  
    print('stream_start')  
    async for chunk in stream:  
        print(chunk)  
    print('stream_end')  
asyncio.run(go())  
