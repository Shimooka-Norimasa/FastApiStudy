# JSON API（/api/todos/...）をまとめたファイル（SQLModel 版）
# 第11章との違い:
#   - DbConn の代わりに SessionDep を使う
#   - データベースから取り出した値が「TodoRow クラスのオブジェクト」になったので、
#     todo["id"] ではなく todo.id と書く
#   - to_schema() での変換が不要になった（response_model に従って FastAPI が変換してくれる）

from fastapi import APIRouter

import database
from dependencies import ExistingTodo, SessionDep
from schemas import Todo, TodoCreate, TodoUpdate

router = APIRouter(prefix="/api/todos", tags=["ToDo API"])


# 一覧  GET /api/todos
@router.get("", response_model=list[Todo])
def list_todos(session: SessionDep):
    return database.get_all_todos(session)


# 1件取得  GET /api/todos/1
@router.get("/{todo_id}", response_model=Todo)
def read_todo(todo: ExistingTodo):
    return todo


# 追加  POST /api/todos
@router.post("", response_model=Todo, status_code=201)
def create_todo(data: TodoCreate, session: SessionDep):
    return database.add_todo(session, data.title)


# 更新  PATCH /api/todos/1
@router.patch("/{todo_id}", response_model=Todo)
def update_todo(todo: ExistingTodo, data: TodoUpdate, session: SessionDep):
    title = data.title if data.title is not None else todo.title
    done = data.done if data.done is not None else todo.done
    return database.update_todo(session, todo, title, done)


# 削除  DELETE /api/todos/1
@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo: ExistingTodo, session: SessionDep):
    database.delete_todo(session, todo)
