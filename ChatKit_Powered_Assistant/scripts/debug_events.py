import asyncio
from app.server import MyChatKitServer
from app.store import SQLiteStore
from app.types import RequestContext
from chatkit.types import UserMessageItem, UserMessageTextContent, ThreadMetadata
async def main():
    store = SQLiteStore()
    await store.connect()
    server = MyChatKitServer(store=store, attachment_store=store)
    thread = ThreadMetadata(id='debug-thread', title=None, metadata={})
    item = UserMessageItem(id='debug-user', thread_id='debug-thread', created_at=None, content=[UserMessageTextContent(type='input_text', text='你好')])
    ctx = RequestContext(user_id='demo-user')
    async for event in server.respond(thread, item, ctx):
        print(type(event).__name__, event.model_dump(mode='json') if hasattr(event, 'model_dump') else event)
    await store.close()
asyncio.run(main())
