# 第9章 Pydantic で JSON API を作る

## この章のねらい

- 画面（HTML）ではなく、**プログラムから使うための JSON API** を作る
- FastAPI の土台の1つである **Pydantic** で、データの「形」を定義する

## この章が終わるとできること

- Pydantic モデルで、受け取る JSON・返す JSON の形とルールを定義できる
- GET / POST / PATCH / DELETE を使った ToDo の API を作れる
- `APIRouter` で URL をグループに分けられる
- `/docs` 画面から API を試せる

---

## 9-1. JSON API とは

これまで作ってきたのは、**人がブラウザで見るための** アプリでした。
JSON API は、**プログラム（JavaScript やスマホアプリ、他のサーバーなど）が使うための** 窓口です。

```
【画面】 GET /             → HTML（人が読む）
【API】  GET /api/todos    → [{"id": 1, "title": "牛乳を買う", "done": false}]（プログラムが読む）
```

第2章で辞書を返したときに JSON が返ったのを覚えているでしょうか。それを本格的にしたものです。
API を用意しておくと、第10章のように JavaScript から使えたり、将来スマホアプリを作ったりもできます。

## 9-2. API の URL 設計

API では、同じ URL に対して **HTTP メソッドで操作を区別する** のが一般的です（REST という考え方）。

| メソッド | URL | 処理 | 成功時のコード |
|---|---|---|---|
| GET | `/api/todos` | 一覧 | 200 |
| GET | `/api/todos/{todo_id}` | 1件取得 | 200 |
| POST | `/api/todos` | 追加 | 201 |
| PATCH | `/api/todos/{todo_id}` | 一部を更新 | 200 |
| DELETE | `/api/todos/{todo_id}` | 削除 | 204 |

HTML のフォームは GET と POST しか送れないため、画面用には `/toggle/1` や `/delete/1` のような URL を作っていました。
API ではプログラムから送るので、PATCH や DELETE も使えます。

## 9-3. ファイル構成

```
step09_json_api/
├── main.py           … アプリ本体と画面用の URL（第8章とほぼ同じ）
├── api.py            … JSON API の URL（新規）
├── schemas.py        … Pydantic モデル（新規）
├── dependencies.py   … DbConn など（第8章で main.py にあったものを移動）
├── database.py       … add_todo が id を返す / update_todo を追加
├── templates/
└── static/
```

`DbConn` や `ExistingTodo` は `main.py` と `api.py` の両方で使うので、`dependencies.py` に移しました。

## 9-4. Pydantic とは

**Pydantic**（パイダンティック）は、**型ヒントを使ってデータの形を定義し、チェックしてくれる** ライブラリです。
FastAPI をインストールすると一緒に入ります。第2章で `number: int` と書くだけで数字のチェックができたのも、裏で Pydantic が動いていたからです。

### クラスとは（ざっくり）

Pydantic では **クラス** を使います。クラスは「データの設計図」です。

```python
class Todo(BaseModel):
    id: int
    title: str
    done: bool
```

- `class 名前(BaseModel):` … Pydantic の `BaseModel` を元にして、`Todo` という設計図を作る
- 中に書いた `名前: 型` が、データの項目になる

設計図から実際のデータ（**インスタンス**）を作るときは、関数のように呼び出します。

```python
todo = Todo(id=1, title="牛乳を買う", done=False)
print(todo.title)        # → 牛乳を買う（ドット . で項目を取り出す）

Todo(id="abc", title="x", done=False)   # → エラー！ id が整数ではない
Todo(id="1", title="x", done=0)         # → OK。"1" は 1 に、0 は False に自動で変換される
```

## 9-5. モデルを定義する（`schemas.py`）

用途ごとに3つのモデルを作ります。

```python
from pydantic import BaseModel, ConfigDict, Field

MAX_TITLE_LENGTH = 100


# 追加するときに受け取る JSON の形  例) {"title": "牛乳を買う"}
class TodoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)


# 更新するときに受け取る JSON の形  例) {"done": true}
class TodoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=MAX_TITLE_LENGTH)
    done: bool | None = None


# 返すときの JSON の形  例) {"id": 1, "title": "牛乳を買う", "done": false}
class Todo(BaseModel):
    id: int
    title: str
    done: bool
```

| 書き方 | 意味 |
|---|---|
| `Field(min_length=1, max_length=100)` | 1文字以上100文字以下、というルール |
| `ConfigDict(str_strip_whitespace=True)` | 文字列の前後の空白を自動で取り除く（第7章の `strip()` を自動でやってくれる） |
| `str \| None = None` | 文字列または None。省略したら None |

**なぜモデルを分けるの？**
追加のときは `id` も `done` も送る必要はなく（自動で決まる）、`title` だけで十分です。
更新のときは「`done` だけ変えたい」こともあるので、両方とも省略できるようにしています。
返すときは全部の項目を返します。**用途ごとに必要な項目が違う** ので、モデルを分けるのが一般的です。

> 第7章では `validate_title` を自分で書きましたが、Pydantic を使うと **ルールを宣言するだけ** でチェックしてくれます。

## 9-6. API を作る（`api.py`）

### APIRouter

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/todos", tags=["ToDo API"])
```

`APIRouter` は **URL のグループ** です。`@router.get(...)` のように `app` の代わりに使います。

- `prefix="/api/todos"` … ここで登録する URL の先頭に `/api/todos` が付く
- `tags` … `/docs` 画面での見出し

`main.py` で、このグループをアプリに登録します。

```python
import api

app.include_router(api.router)
```

ファイルが大きくなってきたら、このように機能ごとにファイルを分けます。

### 一覧と1件取得

```python
def to_schema(row) -> Todo:
    """データベースの行(sqlite3.Row)を Pydantic モデルに変換する"""
    return Todo(**dict(row))


@router.get("", response_model=list[Todo])
def list_todos(conn: DbConn):
    return [to_schema(row) for row in database.get_all_todos(conn)]


@router.get("/{todo_id}", response_model=Todo)
def read_todo(todo: ExistingTodo):
    return to_schema(todo)
```

- `response_model=Todo` … **返す JSON の形** を宣言します。FastAPI がこの形に合わせて JSON を作り、`/docs` にも表示されます。
- `list[Todo]` … Todo のリスト、という型
- `Todo(**dict(row))` … `dict(row)` で `{"id": 1, "title": "...", "done": 0}` という辞書にし、`**` で「`id=1, title="...", done=0`」と引数に展開して渡しています。
- `[to_schema(row) for row in ...]` は **リスト内包表記** です。次のコードを1行で書いたものです。
  ```python
  result = []
  for row in database.get_all_todos(conn):
      result.append(to_schema(row))
  ```
- `@router.get("")` の `""` は、prefix そのもの（`/api/todos`）を意味します。

### 追加

```python
@router.post("", response_model=Todo, status_code=201)
def create_todo(data: TodoCreate, conn: DbConn):
    new_id = database.add_todo(conn, data.title)
    return to_schema(database.get_todo(conn, new_id))
```

**引数の型が Pydantic モデルだと、FastAPI はリクエストの本体（body）の JSON をそのモデルとして受け取ります。**

```
POST /api/todos
本体: {"title": "  牛乳を買う  "}
          │
          ▼  Pydantic がチェック・変換
data = TodoCreate(title="牛乳を買う")   ← 空白は取り除かれている
```

ルールに合わない JSON（`{"title": ""}` など）が来ると、関数が呼ばれる前に FastAPI が **422 エラー** を返します。

`database.add_todo` は、追加した行の id を返すように変更しました。

```python
def add_todo(conn: sqlite3.Connection, title: str) -> int:
    cursor = conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    conn.commit()
    return cursor.lastrowid   # 直前の INSERT で自動採番された id
```

### 更新

```python
@router.patch("/{todo_id}", response_model=Todo)
def update_todo(todo: ExistingTodo, data: TodoUpdate, conn: DbConn):
    title = data.title if data.title is not None else todo["title"]
    done = data.done if data.done is not None else bool(todo["done"])
    database.update_todo(conn, todo["id"], title, done)
    return to_schema(database.get_todo(conn, todo["id"]))
```

送られてこなかった項目（`None`）は今の値を使い、送られてきた項目だけを更新しています。
`A if 条件 else B` は第6章で出てきた1行の if です。

### 削除

```python
@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo: ExistingTodo, conn: DbConn):
    database.delete_todo(conn, todo["id"])
```

204 は「成功したが、返す内容はない」という意味なので、何も `return` しません。

## 9-7. 画面と API でエラーの形を変える（`main.py`）

第7章で、エラーを HTML の画面で表示するようにしました。しかし API を使うプログラムにとっては、HTML より JSON の方が扱いやすいです。
そこで、URL が `/api/` で始まるときは FastAPI 標準の JSON のエラーを返すようにしました。

```python
from fastapi.exception_handlers import http_exception_handler as default_http_exception_handler


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return await default_http_exception_handler(request, exc)
    return templates.TemplateResponse(...)   # 第7章と同じ
```

- `request.url.path` … アクセスされた URL のパス部分（`/api/todos/1` など）
- `startswith("/api/")` … その文字列で始まるかどうか
- FastAPI 標準のハンドラーは `async`（非同期）の関数なので、`async def` と `await` を使って呼び出しています。ここは「`async` の関数を呼ぶときの決まった書き方」と思っておけば大丈夫です。

## 9-8. 動かしてみる

```powershell
cd step09_json_api
uvicorn main:app --reload
```

http://127.0.0.1:8000/docs を開きます。

1. **POST /api/todos** を開き「Try it out」→ 本体に `{"title": "牛乳を買う"}` と入力して「Execute」→ 201 と、作られた ToDo が返る
2. **GET /api/todos** で一覧が返る
3. **PATCH /api/todos/{todo_id}** で `todo_id` に 1、本体に `{"done": true}` → `done` が `true` になる
4. **POST** で `{"title": ""}` を送る → 422 と、どこがおかしいかの説明が返る
5. **GET /api/todos/{todo_id}** で 999 → 404 と `{"detail": "指定された ToDo が見つかりません"}`

http://127.0.0.1:8000 の画面も、第8章と同じように使えます。画面で追加した ToDo は API でも見えます（同じデータベースを使っているため）。

> **ブラウザで直接見る**
> GET の API は、ブラウザで http://127.0.0.1:8000/api/todos を開くだけでも確認できます。

## 9-9. 練習問題

1. `GET /api/todos?done=false` のように、クエリパラメータで「未完了だけ」「完了だけ」を絞り込めるようにしてみよう
   - ヒント: `def list_todos(conn: DbConn, done: bool | None = None):`。Python 側で絞り込んでも、SQL の `WHERE` で絞り込んでもよい

## まとめ

- JSON API = プログラムから使うための窓口。メソッド（GET/POST/PATCH/DELETE）で操作を区別する
- Pydantic のモデル（クラス）で、データの形とルールを宣言できる
- 引数の型を Pydantic モデルにすると、リクエスト本体の JSON を受け取れる
- `response_model` で返す JSON の形を宣言する
- `APIRouter` で URL をグループ化し、`include_router` で登録する

➡ 次は [第10章 JavaScript から API を使う](10_JavaScriptからAPIを使う.md)
