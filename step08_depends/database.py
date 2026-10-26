# データベース操作をまとめたファイル
# 第7章との違い: 各関数は自分で接続を作らず、引数 conn で「接続」を受け取る

import sqlite3

DB_NAME = "todo.db"


def get_connection():
    """データベースへの接続を作って返す"""
    # FastAPI は依存関係(get_db)と URL の関数を別のスレッドで実行することがあるため、
    # 作ったスレッド以外からも接続を使えるよう check_same_thread=False にする
    # （1リクエストにつき1つの接続を使うので、この設定でも安全）
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """リクエストごとに接続を作り、処理が終わったら必ず閉じる（Depends で使う）"""
    conn = get_connection()
    try:
        yield conn      # ここで conn を URL の関数に渡す
    finally:
        conn.close()    # レスポンスを返した後に必ず実行される（エラーが起きても）


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


def add_todo(conn: sqlite3.Connection, title: str):
    """1件追加"""
    conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    conn.commit()


def toggle_todo(conn: sqlite3.Connection, todo_id: int):
    """完了/未完了を切り替える"""
    conn.execute("UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,))
    conn.commit()


def delete_todo(conn: sqlite3.Connection, todo_id: int):
    """1件削除"""
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
