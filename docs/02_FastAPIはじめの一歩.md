# 第2章 FastAPI はじめの一歩

## この章のねらい

- Web アプリが動く仕組み（リクエストとレスポンス）を理解する
- FastAPI でサーバーを起動し、ブラウザからアクセスする
- URL から値を受け取る方法（パスパラメータ・クエリパラメータ）を知る

## この章が終わるとできること

- `uvicorn main:app --reload` でサーバーを起動・停止できる
- URL ごとに違う結果（JSON）を返すアプリが作れる
- 自動生成される API ドキュメント画面（`/docs`）を使って動作確認できる

---

## 2-1. Web アプリの仕組み

```
  ブラウザ                                   サーバー (uvicorn + FastAPI)
 ┌────────┐   ① リクエスト                ┌──────────────────────┐
 │        │  GET /hello/taro  ─────────▶  │ URL を見て関数を選ぶ │
 │        │                               │   hello(name="taro") │
 │        │  ◀─────────  ② レスポンス     │   の結果を返す       │
 └────────┘   {"message": "..."}          └──────────────────────┘
```

- **リクエスト**: ブラウザからサーバーへの「この URL をください」というお願い
- **レスポンス**: サーバーからの返事（HTML や JSON）
- **HTTP メソッド**: リクエストの種類。主に次の2つを使います
  - `GET` … データを **取得** する（URL を開く、リンクをクリック）
  - `POST` … データを **送信** する（フォームの送信ボタン）→ 第4章

## 2-2. FastAPI と uvicorn とは

| 名前 | 役割 | たとえ |
|---|---|---|
| **FastAPI** | 「どの URL で何をするか」を書くためのフレームワーク | 料理のレシピ |
| **uvicorn** | 実際にリクエストを受け付けて FastAPI に渡すサーバー | お店の窓口 |

FastAPI の特徴:

- **型ヒントを書くだけで入力チェック** をしてくれる
- **API ドキュメント画面を自動生成** してくれる（`/docs`）
- 書き方がシンプルで、Python の関数をそのまま使える

## 2-3. コードを見る（`step02_fastapi/main.py`）

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello, FastAPI!"}
```

| 行 | 説明 |
|---|---|
| `from fastapi import FastAPI` | FastAPI ライブラリから `FastAPI` クラスを読み込む |
| `app = FastAPI()` | アプリ本体を作り、`app` という変数に入れる |
| `@app.get("/")` | 「`GET /` が来たら下の関数を呼ぶ」と登録（第1章のデコレータ） |
| `def index():` | 呼ばれる関数。名前は自由 |
| `return {...}` | 辞書を返すと **自動で JSON に変換** されてブラウザに返る |

## 2-4. 起動してみる

```powershell
cd C:\FastApiStudy\step02_fastapi
uvicorn main:app --reload
```

- `main:app` … 「`main.py` ファイルの中の `app` 変数」という意味
- `--reload` … ファイルを保存すると自動で再起動してくれる（開発中に便利）

次のように表示されたら起動成功です。

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

ブラウザで http://127.0.0.1:8000 を開くと、次のように表示されます。

```json
{"message":"Hello, FastAPI!"}
```

**停止するときは、ターミナルで `Ctrl + C`** を押します。

> `127.0.0.1` は「自分自身のパソコン」を表す特別なアドレス、`8000` はポート番号（窓口の番号のようなもの）です。

## 2-5. パスパラメータ ― URL の一部を受け取る

```python
@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"こんにちは、{name}さん"}
```

URL の `{name}` の部分が、関数の引数 `name` に入ります。

| アクセスする URL | 結果 |
|---|---|
| `/hello/taro` | `{"message": "こんにちは、taroさん"}` |
| `/hello/花子` | `{"message": "こんにちは、花子さん"}` |

### 型ヒントによる自動チェック

```python
@app.get("/square/{number}")
def square(number: int):
    return {"number": number, "square": number * number}
```

- `/square/5` → `{"number": 5, "square": 25}`
- `/square/abc` → **エラー（422）** が自動で返る

`number: int` と書いただけで、FastAPI が「数字かどうか」をチェックし、
さらに文字列 `"5"` を整数 `5` に変換してくれます。これが FastAPI の大きな特徴です。

## 2-6. クエリパラメータ ― `?a=1&b=2` を受け取る

```python
@app.get("/add")
def add(a: int, b: int = 0):
    return {"result": a + b}
```

URL のパス (`/add`) に書かれていない引数は、自動的に **クエリパラメータ**（URL の `?` 以降）として扱われます。

| アクセスする URL | 結果 |
|---|---|
| `/add?a=3&b=4` | `{"result": 7}` |
| `/add?a=3` | `{"result": 3}`（b は省略したのでデフォルトの 0） |
| `/add` | エラー（a は必須） |

## 2-7. 自動ドキュメント `/docs`

サーバーを起動したまま http://127.0.0.1:8000/docs を開いてみてください。
作った URL の一覧が表示され、「Try it out」ボタンから実際に試せます。
コードを書くだけでこの画面が自動で作られるのも FastAPI の便利な点です。

## 2-8. 練習問題

1. `/bye/{name}` にアクセスすると `{"message": "さようなら、○○さん"}` を返すようにしてみよう
2. `/multiply?a=3&b=4` で掛け算の結果を返すようにしてみよう

（`--reload` を付けているので、保存するだけで反映されます）

## まとめ

- `app = FastAPI()` でアプリを作り、`@app.get("URL")` で関数を登録する
- 起動: `uvicorn main:app --reload` ／ 停止: `Ctrl + C`
- `{name}` はパスパラメータ、それ以外の引数はクエリパラメータ
- 型ヒントを書くと自動でチェック・変換してくれる

➡ 次は [第3章 Jinja2 で HTML を返す](03_Jinja2でHTMLを返す.md)
