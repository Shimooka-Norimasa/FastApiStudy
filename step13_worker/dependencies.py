# main.py と api.py で使う依存関係
# 第11章との違い: sqlite3 の接続(DbConn)の代わりに、SQLModel のセッション(SessionDep)を渡す

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session

import database

SessionDep = Annotated[Session, Depends(database.get_session)]


def get_todo_or_404(todo_id: int, session: SessionDep) -> database.TodoRow:
    todo = database.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="指定された ToDo が見つかりません")
    return todo


ExistingTodo = Annotated[database.TodoRow, Depends(get_todo_or_404)]
