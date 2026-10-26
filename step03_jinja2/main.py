# 第3章: Jinja2 で HTML を返す
# 実行方法（step03_jinja2 フォルダで）:  uvicorn main:app --reload

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# templates フォルダの中にある HTML をテンプレートとして使う設定
templates = Jinja2Templates(directory="templates")


# response_class=HTMLResponse で「この URL は HTML を返す」ことを明示する
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    fruits = ["りんご", "みかん", "ぶどう"]
    # TemplateResponse(リクエスト, テンプレート名, テンプレートに渡す値の辞書)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "Jinja2 のテスト", "user_name": "太郎", "fruits": fruits},
    )


@app.get("/hello/{name}", response_class=HTMLResponse)
def hello(request: Request, name: str):
    return templates.TemplateResponse(request, "hello.html", {"name": name})
