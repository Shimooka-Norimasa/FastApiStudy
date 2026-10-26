# 第6章: FastAPI + Jinja2 + SQLite で作る ToDo アプリ
# 実行方法（C:\FastApiStudy\step06_todo_app で）:  uvicorn main:app --reload

from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database


# アプリの起動時に1回だけ実行したい処理を書く場所
@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()   # 起動時: テーブルを準備
    yield                # ここでアプリが動き続ける
    # yield の後ろに書いた処理は終了時に実行される（今回は何もしない）


app = FastAPI(lifespan=lifespan)

# /static/... の URL で static フォルダ内のファイル(CSSなど)を配信する
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# 一覧表示 (Read)
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    todos = database.get_all_todos()
    return templates.TemplateResponse(request, "index.html", {"todos": todos})


# 追加 (Create)
@app.post("/add")
def add(title: str = Form()):
    database.add_todo(title)
    return RedirectResponse(url="/", status_code=303)


# 完了/未完了の切り替え (Update)
@app.post("/toggle/{todo_id}")
def toggle(todo_id: int):
    database.toggle_todo(todo_id)
    return RedirectResponse(url="/", status_code=303)


# 削除 (Delete)
@app.post("/delete/{todo_id}")
def delete(todo_id: int):
    database.delete_todo(todo_id)
    return RedirectResponse(url="/", status_code=303)
