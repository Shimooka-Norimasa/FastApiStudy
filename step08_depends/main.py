# 第8章: Depends（依存性注入）でデータベース接続を受け取る
# 実行方法（step08_depends フォルダで）:  uvicorn main:app --reload

import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import database

MAX_TITLE_LENGTH = 100

# 「Depends(database.get_db) で受け取る sqlite3.Connection」に DbConn という別名を付ける
# 引数に conn: DbConn と書くだけで、FastAPI が get_db() を呼んで接続を渡してくれる
DbConn = Annotated[sqlite3.Connection, Depends(database.get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
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


# 依存関係は「別の依存関係」を使うこともできる
# ここでは URL の todo_id と DB 接続を受け取り、ToDo が無ければ 404 にする
def get_todo_or_404(todo_id: int, conn: DbConn):
    todo = database.get_todo(conn, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="指定された ToDo が見つかりません")
    return todo


# 「Depends(get_todo_or_404) で受け取る ToDo（sqlite3.Row）」の別名
ExistingTodo = Annotated[sqlite3.Row, Depends(get_todo_or_404)]


# 一覧表示 (Read)
@app.get("/", response_class=HTMLResponse)
def index(request: Request, conn: DbConn):
    todos = database.get_all_todos(conn)
    return templates.TemplateResponse(request, "index.html", {"todos": todos})


# 追加 (Create)
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


# 完了/未完了の切り替え (Update)
# todo: ExistingTodo と書くだけで「存在チェック済みの ToDo」が受け取れる
@app.post("/toggle/{todo_id}")
def toggle(todo: ExistingTodo, conn: DbConn):
    database.toggle_todo(conn, todo["id"])
    return RedirectResponse(url="/", status_code=303)


# 削除 (Delete)
@app.post("/delete/{todo_id}")
def delete(todo: ExistingTodo, conn: DbConn):
    database.delete_todo(conn, todo["id"])
    return RedirectResponse(url="/", status_code=303)
