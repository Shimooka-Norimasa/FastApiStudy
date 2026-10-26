# 第12章 SQLModel でデータベースを扱う

## この章のねらい

- SQL を直接書かずに、Python のクラスでデータベースを操作する **ORM** を知る
- 第11章のテストを使って、大きな書き換えでも動きが変わらないことを確かめる

## この章が終わるとできること

- SQLModel でテーブルをクラスとして定義できる
- 追加・取得・更新・削除を、SQL を書かずに行える
- テストがあることで、安心してリファクタリングできることを体験する

---

## 12-1. ORM とは

これまでは、SQL を文字列で書いていました。

```python
conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
print(row["title"])
```

**ORM**（Object-Relational Mapping）を使うと、テーブルを **Python のクラス**、行を **そのクラスのオブジェクト** として扱えます。

```python
todo = TodoRow(title=title)
session.add(todo)

todo = session.get(TodoRow, todo_id)
print(todo.title)
```

| | SQL を直接書く | ORM |
|---|---|---|
| 書くもの | SQL の文字列 | Python のコード |
| タイプミス | 実行するまで気づかない（`"titel"` など） | エディタが教えてくれる（`todo.titel`） |
| 結果の扱い | `row["title"]` | `todo.title` |
| データベースの種類を変える | SQL の方言を書き直すことも | 接続先を変えるだけで済むことが多い |
| 注意点 | — | 裏でどんな SQL が動くか意識しにくい |

Python で有名な ORM は **SQLAlchemy** です。
この章で使う **SQLModel** は、SQLAlchemy と Pydantic（第9章）を組み合わせたライブラリで、FastAPI の作者が作っています。
**Pydantic と同じ書き方でテーブルを定義できる** のが特徴です。

## 12-2. 準備

```powershell
pip install sqlmodel
```

## 12-3. ファイル構成と変更点

```
step12_sqlmodel/
├── database.py        … SQLModel で書き直し（★大きく変更）
├── dependencies.py    … DbConn → SessionDep（小さな変更）
├── api.py             … todo["id"] → todo.id など（小さな変更）
├── conftest.py        … 差し替える対象を engine に（小さな変更）
├── test_main.py       … 第11章から1行も変えていない
└── main.py ほか       … 第11章と同じ
```

## 12-4. テーブルの定義（`database.py`）

```python
from sqlmodel import Field, Session, SQLModel, col, create_engine, select

DB_URL = "sqlite:///todo.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


class TodoRow(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False
```

| 部分 | 説明 |
|---|---|
| `DB_URL = "sqlite:///todo.db"` | 接続先。「SQLite の `todo.db` ファイル」という意味 |
| `create_engine(...)` | **エンジン**: データベースへの接続を管理するオブジェクト。アプリ全体で1つ作る |
| `class TodoRow(SQLModel, table=True)` | `table=True` で「テーブルを表すクラス」になる |
| `__tablename__ = "todos"` | テーブル名（書かなければクラス名から自動で決まる） |
| `id: int \| None = Field(default=None, primary_key=True)` | 主キー。追加する前は id が決まっていないので None を許す |
| `done: bool = False` | 真偽値。SQLite の 0/1 との変換は SQLModel がやってくれる |

第9章の Pydantic モデルとほとんど同じ書き方です。

第5章で書いた次の SQL と同じ意味になります。

```sql
CREATE TABLE todos (
    id    INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    done  BOOLEAN NOT NULL
)
```

テーブルの作成も1行です。

```python
def init_db():
    SQLModel.metadata.create_all(engine)
```

`table=True` のクラスを見て、無いテーブルを作ってくれます（第5章の `CREATE TABLE IF NOT EXISTS` と同じく、既にあるテーブルは変更しません）。

## 12-5. セッション

```python
def get_session():
    with Session(engine) as session:
        yield session
```

**セッション** は、データベースとのやり取りを1まとまりで行う単位です。第8章の接続 `conn` にあたります。
`with` を抜けると自動で閉じられるので、第8章の `try` / `finally` が不要になりました。

`dependencies.py` では、`DbConn` の代わりに `SessionDep` を用意します。

```python
SessionDep = Annotated[Session, Depends(database.get_session)]
```

## 12-6. CRUD を書き換える

### 取得（Read）

```python
def get_all_todos(session: Session) -> list[TodoRow]:
    statement = select(TodoRow).order_by(col(TodoRow.id).desc())
    return list(session.exec(statement).all())


def get_todo(session: Session, todo_id: int) -> TodoRow | None:
    return session.get(TodoRow, todo_id)
```

| SQLModel | SQL |
|---|---|
| `select(TodoRow)` | `SELECT * FROM todos` |
| `.order_by(col(TodoRow.id).desc())` | `ORDER BY id DESC` |
| `.where(TodoRow.done == False)` | `WHERE done = 0`（今回は未使用） |
| `session.exec(文).all()` | 実行して全件取得（`fetchall`） |
| `session.get(TodoRow, 1)` | 主キーで1件取得。無ければ None |

`col(...)` は、`TodoRow.id` を「列」として扱うための関数です（`.desc()` などを使うときに付けます）。

### 追加（Create）

```python
def add_todo(session: Session, title: str) -> TodoRow:
    todo = TodoRow(title=title)
    session.add(todo)       # 追加の予約
    session.commit()        # 確定（ここで INSERT が実行される）
    session.refresh(todo)   # データベースから最新の値（自動採番された id など）を読み直す
    return todo
```

オブジェクトを作って `add` → `commit` するだけです。`refresh` で、データベースが決めた id が `todo.id` に入ります。

### 更新（Update）

```python
def update_todo(session: Session, todo: TodoRow, title: str, done: bool) -> TodoRow:
    todo.title = title
    todo.done = done
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
```

**オブジェクトの属性を書き換えて commit するだけ** で、`UPDATE` が実行されます。

### 削除（Delete）

```python
def delete_todo(session: Session, todo: TodoRow):
    session.delete(todo)
    session.commit()
```

第11章までは「id を受け取る」関数でしたが、ORM では「オブジェクトを受け取る」形が自然なので、そう変えています。

## 12-7. API 側の変更（`api.py`）

```python
@router.get("", response_model=list[Todo])
def list_todos(session: SessionDep):
    return database.get_all_todos(session)


@router.patch("/{todo_id}", response_model=Todo)
def update_todo(todo: ExistingTodo, data: TodoUpdate, session: SessionDep):
    title = data.title if data.title is not None else todo.title
    done = data.done if data.done is not None else todo.done
    return database.update_todo(session, todo, title, done)
```

- `todo["title"]` → `todo.title` になりました
- `bool(todo["done"])` の変換が不要になりました（最初から `True` / `False`）
- 第9章の `to_schema()` も不要になりました。`TodoRow` のオブジェクトをそのまま返せば、`response_model=Todo` に従って FastAPI が JSON に変換してくれます

## 12-8. テストで確かめる

テストの準備（`conftest.py`）だけ、差し替える対象を変えます。

```python
@pytest.fixture
def client(tmp_path, monkeypatch):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    monkeypatch.setattr(database, "engine", test_engine)

    with TestClient(app) as test_client:
        yield test_client

    test_engine.dispose()   # 後片付け: エンジンが持っている接続を閉じる
```

第11章では `DB_NAME` を差し替えていましたが、今回は `engine` を差し替えます。
`get_session()` と `init_db()` は呼ばれるたびに `engine` を見るので、テスト用のデータベースが使われます。

**`test_main.py` は第11章から1行も変えていません。** 実行してみましょう。

```powershell
cd step12_sqlmodel
pytest -v
```

```
========================= 16 passed in 1.20s =========================
```

`database.py` を丸ごと書き換えたのに、同じテストがすべて通りました。
つまり **「外から見た動きは第11章と同じ」** ことが確認できたわけです。これがテストを先に書いておく大きなメリットです。

もちろん、アプリとしても動きます。

```powershell
uvicorn main:app --reload
```

> **注意: 既存の todo.db について**
> 各章のフォルダはそれぞれ別の `todo.db` を使うので、第11章までのデータとは混ざりません。
> もしテーブルの定義を変えた（列を追加した）ときは、第6章の練習問題と同じく `todo.db` を削除してから起動し直してください。
> 本格的なアプリでは、データを残したままテーブルを変更する **マイグレーション**（Alembic というツールなど）を使います。

## 12-9. 練習問題

1. `TodoRow` に `created_at: datetime` 列を追加し、追加した日時を記録しよう
   - ヒント: `from datetime import datetime` と `created_at: datetime = Field(default_factory=datetime.now)`
   - `schemas.py` の `Todo` にも `created_at: datetime` を追加すると、API の結果に含まれる
   - テストの `{"id": 1, "title": "...", "done": False}` と比べている部分は失敗するようになるので、テストも直そう（**仕様を変えたらテストも変える**）
2. `GET /api/todos?done=false` の絞り込みを、`select(...).where(...)` で作ってみよう

## まとめ

- ORM = テーブルをクラス、行をオブジェクトとして扱う仕組み
- SQLModel は Pydantic と同じ書き方でテーブルを定義できる
- エンジン（接続の管理）とセッション（やり取りの単位）を使う
- 追加は `add` → `commit`、更新は属性を変えて `commit`、削除は `delete` → `commit`
- テストがあれば、大きな書き換えでも動きが変わらないことをすぐ確かめられる

---

## 応用編を終えて

お疲れさまでした！ 応用編では、基本編の ToDo アプリに次のことを積み上げました。

```
第7章  入力チェック・エラー画面        … 壊れにくくする
第8章  Depends                        … コードを整理する
第9章  Pydantic + JSON API            … プログラムから使えるようにする
第10章 JavaScript                     … 画面をなめらかにする
第11章 テスト                         … 動くことを自動で確かめる
第12章 SQLModel                       … データベース操作を Python らしくする
```

さらに学ぶなら、[付録](付録.md) の「次に学ぶとよいこと」を参考にしてください。
