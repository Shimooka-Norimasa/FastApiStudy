# 第6章 ToDo アプリを完成させる（FastAPI + Jinja2 + SQLite）

## この章のねらい

- 第3章（Jinja2）、第4章（フォーム）、第5章（SQLite）を組み合わせる
- 役割ごとにファイルを分ける考え方を知る

## この章が終わるとできること

- ブラウザから ToDo の **追加・一覧・完了切り替え・削除（CRUD すべて）** ができるアプリを作れる
- サーバーを再起動してもデータが残る（SQLite に保存される）
- CSS などの静的ファイルを配信できる

---

## 6-1. 完成するもの

```
ToDo リスト
[やることを入力              ] [追加]
┌──────────────────────────────────┐
│ 牛乳を買う           [完了] [削除] │
│ ~~勉強する~~         [戻す] [削除] │
└──────────────────────────────────┘
```

## 6-2. フォルダ構成と役割分担

```
step06_todo_app/
├── main.py          … URL と処理の対応（FastAPI）
├── database.py      … データベース操作（SQLite）
├── templates/       … 画面（Jinja2）
│   ├── base.html
│   └── index.html
├── static/          … CSS など、そのまま配信するファイル
│   └── style.css
└── todo.db          … 起動すると自動で作られる
```

全体の流れ:

```
 ブラウザ ──リクエスト──▶ main.py ──呼び出し──▶ database.py ──SQL──▶ todo.db
    ▲                       │                       │
    │                       │◀─────データ───────────┘
    │                       ▼
    └──────HTML──────── templates/index.html
```

第4章では `main.py` にすべて書いていましたが、データベースの処理を `database.py` に分けました。
**「URL と画面の担当」と「データ保存の担当」を分ける** と、どこに何が書いてあるかがわかりやすくなります。

## 6-3. URL の設計

| メソッド | URL | 処理 | CRUD |
|---|---|---|---|
| GET | `/` | 一覧を表示 | Read |
| POST | `/add` | 追加 | Create |
| POST | `/toggle/{todo_id}` | 完了⇔未完了の切り替え | Update |
| POST | `/delete/{todo_id}` | 削除 | Delete |

## 6-4. `database.py` ― データベース担当

```python
import sqlite3

DB_NAME = "todo.db"


def get_connection():
    """データベースへの接続を作って返す"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
```

接続の作り方を関数にまとめ、毎回同じ設定で接続できるようにしています。
`"""..."""` で関数の最初に書いた文字列は **docstring**（関数の説明文）です。

```python
def init_db():
    """テーブルが無ければ作る（アプリ起動時に1回呼ぶ）"""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT    NOT NULL,
            done  INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
```

- `done` … 完了なら 1、未完了なら 0。SQLite には専用の真偽値型が無いので整数で表します。
- `DEFAULT 0` … 値を指定しなければ 0（未完了）になる

```python
def get_all_todos():
    """全件取得（新しい順）"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def add_todo(title: str):
    """1件追加"""
    conn = get_connection()
    conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()


def toggle_todo(todo_id: int):
    """完了/未完了を切り替える（done が 0 なら 1、1 なら 0 にする）"""
    conn = get_connection()
    conn.execute("UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()


def delete_todo(todo_id: int):
    """1件削除"""
    ...（同様）
```

第5章とまったく同じ「接続 → 実行 → commit → close」の流れを、操作ごとに関数にしただけです。
`done = 1 - done` は、0 なら 1、1 なら 0 になる計算で切り替えています。

## 6-5. `main.py` ― URL と処理の担当

### 準備部分

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database
```

`import database` で、自分で作った `database.py` を読み込みます。
中の関数は `database.add_todo(...)` のように `ファイル名.関数名` で呼び出します。

### 起動時の処理（lifespan）

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()   # 起動時: テーブルを準備
    yield                # ここでアプリが動き続ける


app = FastAPI(lifespan=lifespan)
```

アプリ起動時に1回だけテーブルを作りたいので、FastAPI の **lifespan** という仕組みを使っています。

- `yield` より **前** … サーバー起動時に実行される
- `yield` より **後** … サーバー終了時に実行される（今回は無し）

`async` や `@asynccontextmanager` は少し難しい Python の機能ですが、
ここは **「起動時の処理を書く決まった形」** として覚えてしまって大丈夫です。

### 静的ファイルの配信

```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

`static` フォルダの中身を `/static/...` という URL でそのまま配信します。
これで `/static/style.css` で CSS を読み込めるようになります。

### 一覧表示（Read）

```python
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    todos = database.get_all_todos()
    return templates.TemplateResponse(request, "index.html", {"todos": todos})
```

第4章ではリスト `memos` を渡していましたが、ここではデータベースから取ってきた `todos` を渡しています。**違いはデータの出どころだけ** です。

### 追加（Create）

```python
@app.post("/add")
def add(title: str = Form()):
    database.add_todo(title)
    return RedirectResponse(url="/", status_code=303)
```

第4章の `memos.append(content)` が `database.add_todo(title)` に変わっただけです。

### 切り替え・削除（Update / Delete）

```python
@app.post("/toggle/{todo_id}")
def toggle(todo_id: int):
    database.toggle_todo(todo_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{todo_id}")
def delete(todo_id: int):
    database.delete_todo(todo_id)
    return RedirectResponse(url="/", status_code=303)
```

**どの ToDo を操作するか** を、第2章のパスパラメータ `{todo_id}` で受け取っています。
`todo_id: int` なので、数字以外が来たら FastAPI が自動でエラーにしてくれます。

## 6-6. テンプレート

### `base.html`（抜粋）

```html
<link rel="stylesheet" href="{{ url_for('static', path='style.css') }}">
```

`url_for('static', path='style.css')` は、`app.mount(..., name="static")` で登録した場所の URL（`/static/style.css`）を作ってくれる関数です。

### `index.html`

```html
{% extends "base.html" %}

{% block content %}
    <h1>ToDo リスト</h1>

    <form action="/add" method="post" class="add-form">
        <input type="text" name="title" placeholder="やることを入力" required>
        <button type="submit">追加</button>
    </form>

    <ul class="todo-list">
    {% for todo in todos %}
        <li class="{{ 'done' if todo.done else '' }}">
            <span class="title">{{ todo.title }}</span>

            <form action="/toggle/{{ todo.id }}" method="post">
                <button type="submit">{{ '戻す' if todo.done else '完了' }}</button>
            </form>
            <form action="/delete/{{ todo.id }}" method="post">
                <button type="submit" class="delete">削除</button>
            </form>
        </li>
    {% else %}
        <li class="empty">やることはありません</li>
    {% endfor %}
    </ul>
{% endblock %}
```

ポイント:

- `todo.title` … データベースの行（`sqlite3.Row`）から列の値を取り出しています。`todo["title"]` と書いても同じです。
- `'done' if todo.done else ''` … **1行で書く if**（条件式）。`done` が 1 なら `'done'`、0 なら空文字になります。CSS で `done` クラスに打ち消し線を付けています。
- `action="/toggle/{{ todo.id }}"` … ToDo ごとに送信先 URL を変えています。id が 3 なら `/toggle/3` に送られます。
- 削除や切り替えも **データを変更する操作なので POST**（リンク `<a>` ではなくフォームのボタン）にしています。

## 6-7. 動かしてみる

```powershell
cd step06_todo_app
uvicorn main:app --reload
```

http://127.0.0.1:8000 を開いて、

1. ToDo をいくつか追加する
2. 「完了」を押すと打ち消し線になる、「戻す」で元に戻る
3. 「削除」で消える
4. **`Ctrl + C` でサーバーを止めて再起動しても、データが残っている！**（第4章との違い）

フォルダに `todo.db` ができています。これを削除すると、データがすべてリセットされます。

## 6-8. 1回のリクエストで何が起きているか（追加ボタンの場合）

```
1. ブラウザ: 「追加」ボタン → POST /add (title=牛乳を買う)
2. main.py:  @app.post("/add") の add() が呼ばれる。title に "牛乳を買う" が入る
3. database.py: add_todo() が INSERT を実行して commit
4. main.py:  RedirectResponse で「/ を開き直して」と返す
5. ブラウザ: GET / を送る
6. main.py:  index() が呼ばれ、database.get_all_todos() で全件取得
7. Jinja2:   index.html に todos を埋め込んで HTML を作る
8. ブラウザ: 新しい一覧が表示される
```

この流れが理解できれば、この教材のゴールは達成です！

## 6-9. 練習問題（機能追加）

難しさの順に並べています。

1. **件数表示**: 一覧の上に「全 ○ 件」と表示する（ヒント: `{{ todos | length }}`）
2. **未完了の件数**: 「未完了 ○ 件」も表示する（ヒント: Python 側で数えて渡す、または SQL で `SELECT COUNT(*) FROM todos WHERE done = 0`）
3. **作成日時**: テーブルに `created_at TEXT` 列を追加して日時を記録・表示する
   - 列を追加したら、古い `todo.db` を削除してから起動し直すこと（`CREATE TABLE IF NOT EXISTS` は既存のテーブルを変更しないため）
   - ヒント: `from datetime import datetime` → `datetime.now().strftime("%Y-%m-%d %H:%M")`
4. **編集機能**: タイトルを変更できる画面（`GET /edit/{todo_id}` で編集フォーム、`POST /edit/{todo_id}` で更新）を作る

## まとめ

- 第4章のリストを、第5章の SQLite に置き換えるとデータが永続化される
- `main.py`（URL・画面）と `database.py`（データ）に役割を分けた
- 起動時の処理は `lifespan`、CSS は `StaticFiles` で配信
- 操作対象の ID は URL のパスパラメータで受け取る

これで **基本編は終わり** です。お疲れさまでした！

➡ 次は応用編 [第7章 入力チェックとエラー表示](07_入力チェックとエラー表示.md)（困ったときは [付録](付録.md)）
