import os
import shutil

# Remove proxy env vars so internal OpenAI/httpx clients do not try to use a local proxy.
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("ALL_PROXY", None)
os.environ.pop("NO_PROXY", None)
os.environ.pop("no_proxy", None)
os.environ.pop("VISION_ROUTER_FORCE_PROXY", None)
import base64
import asyncio
from pathlib import Path
from uuid import uuid4
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, UploadFile, Depends, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import AsyncOpenAI
import aiofiles

from chatkit.server import StreamingResult
from chatkit.types import FileAttachment, ImageAttachment

from app.server import MyChatKitServer
from app.store import SQLiteStore
from app.types import RequestContext

load_dotenv()
for _proxy_name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY", "no_proxy", "VISION_ROUTER_FORCE_PROXY"):
    if os.getenv(_proxy_name) is not None:
        os.environ[_proxy_name] = os.environ[_proxy_name].strip()
import httpx

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    http_client=httpx.AsyncClient(proxy=None, trust_env=False),
)

import logging
logging.basicConfig(level=logging.INFO)

for _name in (
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "DEFAULT_MODEL",
    "OPENAI_DEFAULT_MODEL",
    "OPENAI_TRACING",
):
    if os.getenv(_name) is not None:
        os.environ[_name] = os.environ[_name].strip()

try:
    from chatkit.agents import stream_agent_response as _stream_agent_response

    async def _logged_stream_agent_response(agent_context, result, *, converter=None, **kwargs):
        try:
            async for event in _stream_agent_response(
                agent_context,
                result,
                converter=converter,
                **kwargs,
            ):
                yield event
        except Exception as exc:
            user_id = getattr(getattr(agent_context, "request_context", None), "user_id", "unknown")
            response = getattr(exc, "response", None)
            print(
                "[stream_agent_response][user=%s] error=%s: %s\nresponse=%s",
                user_id,
                type(exc).__name__,
                exc,
                response,
            )
            raise

    import chatkit.agents as _chatkit_agents
    _chatkit_agents.stream_agent_response = _logged_stream_agent_response
except Exception as exc:  # pragma: no cover - instrumentation only
    print(f"[instrument][stream_agent_response] skipped: {exc}")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize store globally, but connect in lifespan
store = SQLiteStore()
server = MyChatKitServer(store=store, attachment_store=store)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    await store.connect()
    yield
    # Shutdown: Close DB
    await store.close()

app = FastAPI(lifespan=lifespan)

# --- Enable CORS ---
@app.get('/__debug_env')
async def debug_env():
    return {
        'default_model': os.getenv('DEFAULT_MODEL'),
        'openai_default_model': os.getenv('OPENAI_DEFAULT_MODEL'),
        'openai_base_url': os.getenv('OPENAI_BASE_URL'),
        'openai_api_key_prefix': (os.getenv('OPENAI_API_KEY') or '')[:12],
        'openai_api_key_len': len(os.getenv('OPENAI_API_KEY') or ''),
        'openai_api_key_suffix': (os.getenv('OPENAI_API_KEY') or '')[-4:],
    }

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user(request: Request) -> RequestContext:
    user_id = request.headers.get("x-chatkit-user")
    if not user_id:
        user_id = "anonymous-default"
    return RequestContext(user_id=user_id)

@app.post("/chatkit")
async def handle_chatkit(request: Request, ctx: RequestContext = Depends(get_user)):
    try:
        body = await request.body()
        result = await server.process(body, ctx)
        
        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        else:
            return Response(content=result.json, media_type="application/json")
            
    except Exception as e:
        print(f"Error processing request: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/upload")
async def upload_file(file: UploadFile, ctx: RequestContext = Depends(get_user)):
    file_id = f"file_{uuid4().hex}"
    ext = Path(file.filename).suffix
    safe_filename = f"{file_id}{ext}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Non-blocking file write
    async with aiofiles.open(file_path, "wb") as f:
        while content := await file.read(1024 * 1024):  # Read in 1MB chunks
            await f.write(content)
        
    is_image = file.content_type.startswith("image/")
    
    if is_image:
        # Non-blocking read for preview generation
        async with aiofiles.open(file_path, "rb") as f:
            file_bytes = await f.read()
            b64_data = base64.b64encode(file_bytes).decode("utf-8")
            preview_data_url = f"data:{file.content_type};base64,{b64_data}"
            
        attachment = ImageAttachment(
            type="image", 
            id=file_id, 
            name=file.filename,
            mime_type=file.content_type, 
            preview_url=preview_data_url, 
                url=f"/files/{safe_filename}"
        )
    else:
        attachment = FileAttachment(
            type="file", 
            id=file_id, 
            name=file.filename,
            mime_type=file.content_type, 
                url=f"/files/{safe_filename}"
        )
        
    await store.save_attachment(attachment, ctx)
    return attachment.model_dump(mode="json")

app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Workers=1 is fine for async, but ensure reload is off in actual production
    uvicorn.run("main:app", host="0.0.0.0", port=8011, reload=True)