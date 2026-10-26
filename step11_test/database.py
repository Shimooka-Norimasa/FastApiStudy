# データベース操作をまとめたファイル
# 第8章との違い: add_todo が新しい id を返す / update_todo を追加

import sqlite3

DB_NAME = "todo.db"


def get_connection():
    """データベースへの接続を作って返す"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """リクエストごとに接続を作り、処理が終わったら必ず閉じる（Depends で使う）"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


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


def get_all_todos(conn: sqlite3.Connection):
    """全件取得（新しい順）"""
    return conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()


def get_todo(conn: sqlite3.Connection, todo_id: int):
    """1件取得。見つからなければ None を返す"""
    return conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()


def add_todo(conn: sqlite3.Connection, title: str) -> int:
    """1件追加し、追加した行の id を返す"""
    cursor = conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    conn.commit()
    return cursor.lastrowid   # 直前の INSERT で自動採番された id


def update_todo(conn: sqlite3.Connection, todo_id: int, title: str, done: bool):
    """タイトルと完了状態を更新する"""
    conn.execute(
        "UPDATE todos SET title = ?, done = ? WHERE id = ?",
        (title, int(done), todo_id),   # True/False を 1/0 にして保存
    )
    conn.commit()


def toggle_todo(conn: sqlite3.Connection, todo_id: int):
    """完了/未完了を切り替える"""
    conn.execute("UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,))
    conn.commit()


def delete_todo(conn: sqlite3.Connection, todo_id: int):
    """1件削除"""
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
