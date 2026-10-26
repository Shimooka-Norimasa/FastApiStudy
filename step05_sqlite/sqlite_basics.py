# 第5章: Python から SQLite を使う（Web なしで単体で動かす）
# 実行方法（C:FastApiStudystep05_sqlite で）:  python sqlite_basics.py
# 同じフォルダに sample.db というファイルが作られる

import sqlite3

# データベースに接続する（ファイルが無ければ自動で作られる）
conn = sqlite3.connect("sample.db")

# 結果を「列名でアクセスできる形」で受け取る設定（row["name"] のように書ける）
conn.row_factory = sqlite3.Row

# ---------- テーブル作成 (CREATE) ----------
conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age  INTEGER
    )
""")

# 毎回同じ結果になるよう、いったん中身を空にしておく
conn.execute("DELETE FROM users")

# ---------- 追加 (INSERT) ----------
# 値は ? で書き、後ろのタプルで渡す（SQLインジェクション対策。必ずこう書く）
conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("太郎", 20))
conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("花子", 25))
conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("次郎", 18))
conn.commit()   # commit で変更を確定（これを忘れると保存されない）

# ---------- 取得 (SELECT) ----------
print("=== 全員 ===")
rows = conn.execute("SELECT id, name, age FROM users ORDER BY id").fetchall()
for row in rows:
    print(row["id"], row["name"], row["age"])

print("=== 20歳以上 ===")
rows = conn.execute("SELECT * FROM users WHERE age >= ?", (20,)).fetchall()
for row in rows:
    print(row["name"])

# ---------- 更新 (UPDATE) ----------
conn.execute("UPDATE users SET age = ? WHERE name = ?", (21, "太郎"))
conn.commit()

# fetchone は 1件だけ取得（無ければ None）
row = conn.execute("SELECT * FROM users WHERE name = ?", ("太郎",)).fetchone()
print("=== 更新後の太郎 ===")
print(dict(row))   # dict() で普通の辞書に変換できる

# ---------- 削除 (DELETE) ----------
conn.execute("DELETE FROM users WHERE name = ?", ("次郎",))
conn.commit()

count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
print(f"=== 削除後の人数: {count} ===")

# 接続を閉じる
conn.close()
