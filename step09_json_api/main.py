# 第9章: Pydantic で JSON API を作る
# 実行方法（step09_json_api フォルダで）:  uvicorn main:app --reload
# HTML 画面: http://127.0.0.1:8000   API の確認: http://127.0.0.1:8000/docs

from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request
from fastapi.exception_handlers import http_exception_handler as default_http_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import api
import database
from dependencies import DbConn, ExistingTodo
from schemas import MAX_TITLE_LENGTH


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# api.py の URL（/api/todos/...）をアプリに登録する
app.include_router(api.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # API へのリクエストなら、FastAPI 標準の JSON エラー {"detail": "..."} を返す
    if request.url.path.startswith("/api/"):
        return await default_http_exception_handler(request, exc)
    # それ以外（画面）は HTML のエラー画面を返す
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )


def validate_title(title: str) -> str | None:
    """タイトルをチェックし、問題があればエラーメッセージを返す（問題なければ None）"""
    if title == "":
        return "やることを入力してください"
    if len(title) > MAX_TITLE_LENGTH:
        return f"{MAX_TITLE_LENGTH}文字以内で入力してください（現在 {len(title)} 文字）"
    return None


# ----- ここから下は第8章と同じ（HTML 画面用） -----

@app.get("/", response_class=HTMLResponse)
def index(request: Request, conn: DbConn):
    todos = database.get_all_todos(conn)
    return templates.TemplateResponse(request, "index.html", {"todos": todos})


@app.post("/add", response_class=HTMLResponse)
def add(request: Request, conn: DbConn, title: str = Form()):
    title = title.strip()

    error = validate_title(title)
    if error:
        todos = database.get_all_todos(conn)
        return templates.TemplateResponse(
            request,
            "index.html",
            {"todos": todos, "error": error, "title": title},
            status_code=400,
        )

    database.add_todo(conn, title)
    return RedirectResponse(url="/", status_code=303)


@app.post("/toggle/{todo_id}")
def toggle(todo: ExistingTodo, conn: DbConn):
    database.toggle_todo(conn, todo["id"])
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{todo_id}")
def delete(todo: ExistingTodo, conn: DbConn):
    database.delete_todo(conn, todo["id"])
    return RedirectResponse(url="/", status_code=303)
