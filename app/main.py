import os
from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from app.apis.practice_apis import router as practice_router

app = FastAPI()

app.include_router(practice_router)

BASE_DIR = Path(__file__).resolve().parent.parent

if not (BASE_DIR / "static").exists():
    os.mkdir(BASE_DIR / "static")
if not (BASE_DIR / "media").exists():
    os.mkdir(BASE_DIR / "media")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")


@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    if (
        path.startswith("api/v1")
        or path.startswith("static/")
        or path.startswith("media/")
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / "static" / "index.html")