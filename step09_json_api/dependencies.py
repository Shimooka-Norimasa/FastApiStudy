# main.py と api.py の両方で使う依存関係（第8章で main.py に書いていたもの）を置くファイル

import sqlite3
from typing import Annotated

from fastapi import Depends, HTTPException

import database

DbConn = Annotated[sqlite3.Connection, Depends(database.get_db)]


def get_todo_or_404(todo_id: int, conn: DbConn):
    todo = database.get_todo(conn, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="指定された ToDo が見つかりません")
    return todo


ExistingTodo = Annotated[sqlite3.Row, Depends(get_todo_or_404)]
