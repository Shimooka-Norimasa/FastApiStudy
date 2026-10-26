# 第7章: 入力チェックとエラー表示
# 実行方法（step07_validation フォルダで）:  uvicorn main:app --reload

from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import database

MAX_TITLE_LENGTH = 100


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# HTTPException が起きたときに、JSON ではなく HTML のエラー画面を返す
# （存在しない URL へのアクセスで FastAPI が出す 404 も、ここで受け取れるよう
#   starlette の HTTPException を指定している）
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


def get_todo_or_404(todo_id: int):
    """ToDo を取得する。見つからなければ 404 エラーにする"""
    todo = database.get_todo(todo_id)
    if todo is None:
        # raise で例外を投げると、その時点で処理が中断され、上の exception_handler が呼ばれる
        raise HTTPException(status_code=404, detail="指定された ToDo が見つかりません")
    return todo


# 一覧表示 (Read)
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    todos = database.get_all_todos()
    return templates.TemplateResponse(request, "index.html", {"todos": todos})


# 追加 (Create)
@app.post("/add", response_class=HTMLResponse)
def add(request: Request, title: str = Form()):
    title = title.strip()   # 前後の空白を取り除く（"   " だけの入力は "" になる）

    error = validate_title(title)
    if error:
        # エラーのときはリダイレクトせず、エラーメッセージと入力値を付けて一覧画面を表示し直す
        todos = database.get_all_todos()
        return templates.TemplateResponse(
            request,
            "index.html",
            {"todos": todos, "error": error, "title": title},
            status_code=400,
        )

    database.add_todo(title)
    return RedirectResponse(url="/", status_code=303)


# 完了/未完了の切り替え (Update)
@app.post("/toggle/{todo_id}")
def toggle(todo_id: int):
    get_todo_or_404(todo_id)
    database.toggle_todo(todo_id)
    return RedirectResponse(url="/", status_code=303)


# 削除 (Delete)
@app.post("/delete/{todo_id}")
def delete(todo_id: int):
    get_todo_or_404(todo_id)
    database.delete_todo(todo_id)
    return RedirectResponse(url="/", status_code=303)
