# 第13章: ワーカーで時間のかかる処理を行う
# 実行方法（C:\FastApiStudy\step13_worker で）:
#   ターミナル1:  uvicorn main:app --reload   … Web アプリ
#   ターミナル2:  python worker.py            … ワーカー
#
# 第12章との違い: CSV 書き出しの API（exports_api.py）を登録しただけ

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler as default_http_exception_handler
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import api
import database
import exports_api
from schemas import MAX_TITLE_LENGTH


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(api.router)
app.include_router(exports_api.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return await default_http_exception_handler(request, exc)
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )


# 画面の「入れ物」だけを返す。ToDo の中身は JavaScript が API から取得して表示する
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"max_length": MAX_TITLE_LENGTH})
