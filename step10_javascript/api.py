# JSON API（/api/todos/...）をまとめたファイル
# HTML 画面用の URL は main.py、プログラム向けの JSON API はこちら、と分けている

from fastapi import APIRouter

import database
from dependencies import DbConn, ExistingTodo
from schemas import Todo, TodoCreate, TodoUpdate

# APIRouter: URL のグループ。ここで登録した URL には先頭に /api/todos が付く
# tags は /docs 画面での見出し
router = APIRouter(prefix="/api/todos", tags=["ToDo API"])


def to_schema(row) -> Todo:
    """データベースの行(sqlite3.Row)を Pydantic モデルに変換する"""
    # dict(row) で {"id": 1, "title": "...", "done": 0} になり、
    # Todo(**辞書) で「キー=値」を引数として渡す。done の 0/1 は自動で false/true になる
    return Todo(**dict(row))


# 一覧  GET /api/todos
# response_model で「返す JSON の形」を宣言する（/docs にも表示される）
@router.get("", response_model=list[Todo])
def list_todos(conn: DbConn):
    return [to_schema(row) for row in database.get_all_todos(conn)]


# 1件取得  GET /api/todos/1
@router.get("/{todo_id}", response_model=Todo)
def read_todo(todo: ExistingTodo):
    return to_schema(todo)


# 追加  POST /api/todos   本体: {"title": "..."}
# 引数の型が Pydantic モデルだと、FastAPI はリクエスト本体の JSON をそのモデルとして受け取る
# status_code=201 は「作成した」という意味のステータスコード
@router.post("", response_model=Todo, status_code=201)
def create_todo(data: TodoCreate, conn: DbConn):
    new_id = database.add_todo(conn, data.title)
    return to_schema(database.get_todo(conn, new_id))


# 更新  PATCH /api/todos/1   本体: {"done": true} など
@router.patch("/{todo_id}", response_model=Todo)
def update_todo(todo: ExistingTodo, data: TodoUpdate, conn: DbConn):
    # 送られてこなかった項目(None)は、今の値をそのまま使う
    title = data.title if data.title is not None else todo["title"]
    done = data.done if data.done is not None else bool(todo["done"])
    database.update_todo(conn, todo["id"], title, done)
    return to_schema(database.get_todo(conn, todo["id"]))


# 削除  DELETE /api/todos/1
# 204 は「成功したが返す内容は無い」という意味
@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo: ExistingTodo, conn: DbConn):
    database.delete_todo(conn, todo["id"])
