import os
from pathlib import Path
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

# 기존 실습용 api 라우터를 불러옵니다.
from app.apis.practice_apis import router as practice_router
# ★ [추가] Canvas에 생성해 둔 Users API 라우터를 새롭게 불러옵니다.
from app.apis.users import router as users_router

# FastAPI 앱 생성 (기존 코드에 중복 작성되어 꼬여 있던 선언부들을 하나로 깨끗하게 정리했습니다!)
app = FastAPI(title="폐렴 환자 관리 백오피스")

# 메인 앱에 각각의 API 라우터들을 연동합니다.
app.include_router(practice_router)
app.include_router(users_router)  # ★ [추가] Users API 라우터 연동 완료!

BASE_DIR = Path(__file__).resolve().parent.parent

# 만약 static, media 폴더가 존재하지 않으면 생성
if not (BASE_DIR / "static").exists():
    os.mkdir(BASE_DIR / "static")
if not (BASE_DIR / "media").exists():
    os.mkdir(BASE_DIR / "media")

# 'static' 폴더를 '/static' 경로로 마운트 (CSS, JS 파일 서빙용)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
# 'media' 폴더를 '/media' 경로로 마운트 (사용자 업로드 파일 서빙용)
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")


@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    # API나 정적 파일 경로는 제외 (FastAPI가 먼저 매칭하지 못한 경우에만 실행됨)
    if (
        path.startswith("api/v1")
        or path.startswith("static/")
        or path.startswith("media/")
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / "static" / "index.html")