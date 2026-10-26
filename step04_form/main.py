# 第4章: フォームでデータを送る（データはメモリ上のリストに保存）
# 実行方法（C:\FastApiStudy\step04_form で）:  uvicorn main:app --reload

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# データの保存先（ただのリスト）。サーバーを止めると消える → 第6章で SQLite に置き換える
memos = []


# 一覧画面（GET）
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"memos": memos})


# フォームの送信先（POST）
# Form() を付けると「HTML フォームから送られた値」として受け取る
# 引数名 content は HTML の <input name="content"> と一致させる
@app.post("/add")
def add(content: str = Form()):
    memos.append(content)
    # 処理が終わったら一覧画面へ移動させる（PRG パターン。詳しくは資料参照）
    # status_code=303 は「別の URL を GET で開き直して」という意味
    return RedirectResponse(url="/", status_code=303)
