# データベース操作をまとめたファイル（第6章 + get_todo を追加）

import sqlite3

DB_NAME = "todo.db"


def get_connection():
    """データベースへの接続を作って返す"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


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


def get_all_todos():
    """全件取得（新しい順）"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def get_todo(todo_id: int):
    """1件取得。見つからなければ None を返す"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return row


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
    conn = get_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
