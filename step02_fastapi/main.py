# 第2章: FastAPI はじめの一歩
# 実行方法（step02_fastapi フォルダで）:  uvicorn main:app --reload
# ブラウザで http://127.0.0.1:8000 を開く

from fastapi import FastAPI

# FastAPI アプリ本体を作る。uvicorn は「main.py の app」を探して起動する
app = FastAPI()


# GET / にアクセスされたらこの関数が呼ばれる
@app.get("/")
def index():
    # 辞書を返すと、FastAPI が自動で JSON に変換してくれる
    return {"message": "Hello, FastAPI!"}


# パスパラメータ: URL の一部 {name} を引数 name として受け取る
# 例) /hello/taro -> {"message": "こんにちは、taroさん"}
@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"こんにちは、{name}さん"}


# 型ヒントが int なので、数字以外が来ると FastAPI が自動でエラー(422)を返す
# 例) /square/5 -> {"number": 5, "square": 25}
@app.get("/square/{number}")
def square(number: int):
    return {"number": number, "square": number * number}


# クエリパラメータ: URL の ? 以降 (?a=1&b=2) を引数として受け取る
# パスに書かれていない引数は、自動的にクエリパラメータになる
# 例) /add?a=3&b=4 -> {"result": 7}
@app.get("/add")
def add(a: int, b: int = 0):
    return {"result": a + b}
