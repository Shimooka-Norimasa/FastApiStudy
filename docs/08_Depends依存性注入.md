# 第8章 Depends（依存性注入）

## この章のねらい

- FastAPI の中心的な機能の1つ **Depends（依存性注入）** を理解する
- 「データベース接続の準備と後片付け」を1か所にまとめる

## この章が終わるとできること

- `Depends` を使って、URL の関数にデータベース接続を自動で渡せる
- 「存在チェック済みの ToDo」を受け取る依存関係を作り、同じチェックを何度も書かずに済ませられる
- `yield` を使って、リクエストの後で必ず後片付けを実行できる

---

## 8-1. 第7章のコードの気になる点

第7章の `database.py` は、どの関数も同じ形をしていました。

```python
def add_todo(title: str):
    conn = get_connection()    # ← 毎回
    conn.execute(...)
    conn.commit()
    conn.close()               # ← 毎回
```

- 1回の画面表示の中で何度も接続・切断をしている（例: エラー時の `add` は2回）
- 途中でエラーが起きると `close()` まで進まず、接続が閉じられない
- `main.py` の `toggle` と `delete` の両方で `get_todo_or_404(todo_id)` を呼んでいる

この章では、これらを **Depends** で整理します。

## 8-2. 依存性注入（Dependency Injection）とは

名前は難しそうですが、考え方はシンプルです。

> **関数が必要とするもの（依存）を、関数の中で自分で用意するのではなく、外から渡してもらう（注入）**

```
【これまで】 関数の中で自分で用意する
  def add(title):
      conn = get_connection()   ← 自分で接続を作る
      ...
      conn.close()              ← 自分で片付ける

【Depends】 FastAPI に用意してもらう
  def add(title, conn: DbConn):   ← 「接続ちょうだい」と引数に書くだけ
      ...                          ← 用意も片付けも FastAPI がやってくれる
```

レストランにたとえると、料理人（URL の関数）が毎回自分で食材を買いに行くのではなく、
「この料理にはトマトが必要」と書いておけば、仕入れ係（FastAPI）がそろえてくれる、というイメージです。

## 8-3. 接続を渡す依存関係を作る（`database.py`）

```python
def get_db():
    """リクエストごとに接続を作り、処理が終わったら必ず閉じる（Depends で使う）"""
    conn = get_connection()
    try:
        yield conn      # ここで conn を URL の関数に渡す
    finally:
        conn.close()    # レスポンスを返した後に必ず実行される（エラーが起きても）
```

### `yield` とは

`return` は値を返して関数が **終わり** ますが、`yield` は値を渡して関数が **一時停止** します。
FastAPI は次の順番で `get_db` を使います。

```
1. get_db() を開始  → conn を作る
2. yield conn       → 一時停止。conn を URL の関数に渡す
3. URL の関数が実行される（add、delete など）
4. レスポンスを返す
5. get_db() を再開  → finally の conn.close() が実行される
```

第6章の `lifespan` の `yield` も同じ考え方でした（`yield` の前が起動時、後が終了時）。

### `try` / `finally` とは

```python
try:
    （処理）
finally:
    （必ず実行したい処理）
```

`try` の中でエラーが起きても起きなくても、`finally` の中は **必ず** 実行されます。
これで「途中でエラーが起きると接続が閉じられない」問題が解決します。

### 各関数は接続を受け取るだけ

```python
def add_todo(conn: sqlite3.Connection, title: str):
    """1件追加"""
    conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    conn.commit()
```

接続を作る・閉じる処理がなくなり、本来の仕事（SQL の実行）だけになりました。

> **`check_same_thread=False` について**
> ```python
> conn = sqlite3.connect(DB_NAME, check_same_thread=False)
> ```
> SQLite の接続は、標準では「作ったスレッド（処理の流れ）以外からは使えない」設定になっています。
> FastAPI は `get_db` と URL の関数を別々のスレッドで実行することがあるため、この制限を外しています。
> 1つのリクエストにつき1つの接続を使うので、外しても安全です。

## 8-4. Depends で受け取る（`main.py`）

```python
import sqlite3
from typing import Annotated

from fastapi import Depends

DbConn = Annotated[sqlite3.Connection, Depends(database.get_db)]
```

- `Depends(database.get_db)` … 「`get_db` を呼んで、その結果を渡してね」という印
- `Annotated[型, 追加情報]` … 型ヒントに追加情報を付ける書き方。ここでは「型は `sqlite3.Connection`、用意の仕方は `Depends(get_db)`」
- 長いので `DbConn` という **別名** を付けています

使う側は、引数に書くだけです。

```python
@app.get("/", response_class=HTMLResponse)
def index(request: Request, conn: DbConn):
    todos = database.get_all_todos(conn)
    return templates.TemplateResponse(request, "index.html", {"todos": todos})
```

> 別名を使わずに `conn: Annotated[sqlite3.Connection, Depends(database.get_db)]` と書いても同じ意味です。
> 古い書き方の `conn: sqlite3.Connection = Depends(database.get_db)` もよく見かけますが、今は `Annotated` を使う書き方が推奨されています。

## 8-5. 依存関係から依存関係を使う

依存関係の関数も、引数に別の依存関係やパスパラメータを書けます。

```python
def get_todo_or_404(todo_id: int, conn: DbConn):
    todo = database.get_todo(conn, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="指定された ToDo が見つかりません")
    return todo


ExistingTodo = Annotated[sqlite3.Row, Depends(get_todo_or_404)]
```

- `todo_id: int` … URL の `{todo_id}` から自動で受け取る
- `conn: DbConn` … さらに `get_db` から接続を受け取る

これで、URL の関数は「存在チェック済みの ToDo」を受け取るだけになります。

```python
@app.post("/delete/{todo_id}")
def delete(todo: ExistingTodo, conn: DbConn):
    database.delete_todo(conn, todo["id"])
    return RedirectResponse(url="/", status_code=303)
```

この関数が呼ばれた時点で「ToDo は必ず存在する」ことが保証されています。

```
POST /delete/3
  │
  ├─ get_db() ─────────────▶ conn
  │                            │
  ├─ get_todo_or_404(3, conn) ─▶ todo（無ければ ここで 404）
  │
  └─ delete(todo, conn) を実行
```

> **同じ接続が使われる**
> `get_todo_or_404` も `delete` も `DbConn` を受け取っていますが、
> FastAPI は1つのリクエストの中では依存関係の結果を使い回すので、`get_db` が呼ばれるのは1回だけです。

## 8-6. 動かしてみる

```powershell
cd C:\FastApiStudy\step08_depends
uvicorn main:app --reload
```

見た目と動きは第7章とまったく同じです。
このように **動きを変えずにコードの構造を良くすること** を **リファクタリング** といいます。

## 8-7. Depends の便利な点

| 便利な点 | 説明 |
|---|---|
| 準備と後片付けを1か所にまとめられる | 接続の close 忘れが起きない |
| 同じ処理を使い回せる | 存在チェックを各関数に書かなくてよい |
| 差し替えができる | テストのときだけ別のデータベースを使う、などが簡単（第11章） |

ログインユーザーの取得、権限チェックなども、Depends で作るのが FastAPI の定番です。

## 8-8. 練習問題

1. `get_todo_or_404` の中に `print(f"ToDo {todo_id} をチェック")` を入れて、削除ボタンを押したときにターミナルに表示されるのを確認しよう
2. `get_db` の `yield` の前後に `print("接続")` と `print("切断")` を入れ、1回の画面表示で何回呼ばれるか確認しよう

## まとめ

- Depends = 関数に必要なものを FastAPI に用意してもらう仕組み
- `yield` を使った依存関係で、準備（前）と後片付け（後）を書ける
- `Annotated[型, Depends(関数)]` に別名を付けると、引数に書くだけで使える
- 依存関係は別の依存関係を使える（チェックを部品化できる）

➡ 次は [第9章 Pydantic で JSON API を作る](09_PydanticでJSON_APIを作る.md)
