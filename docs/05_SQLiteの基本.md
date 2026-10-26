# 第5章 SQLite の基本

## この章のねらい

- Web とは切り離して、Python から SQLite を操作する方法だけを学ぶ
- データの追加・取得・更新・削除（CRUD）の SQL を一通り体験する

## この章が終わるとできること

- Python の `sqlite3` でデータベースに接続し、テーブルを作れる
- `INSERT` / `SELECT` / `UPDATE` / `DELETE` を実行できる
- `?` を使った安全な値の渡し方がわかる

---

## 5-1. SQLite とは（さらっと）

- データベースの一種。**データベース全体が1つのファイル**（例: `sample.db`）になる
- サーバーを別に立てる必要がなく、**Python に標準で付いている**（`import sqlite3` だけで使える）
- 学習や小さなアプリにぴったり

データは **テーブル**（表）に保存します。Excel のシートのようなものです。

```
users テーブル
┌────┬──────┬─────┐
│ id │ name │ age │   ← 列（カラム）
├────┼──────┼─────┤
│  1 │ 太郎 │  20 │   ← 行（レコード）
│  2 │ 花子 │  25 │
└────┴──────┴─────┘
```

テーブルの操作には **SQL** という専用の言語を使います。

| 操作 | SQL | 意味 |
|---|---|---|
| Create | `INSERT INTO ...` | 追加 |
| Read | `SELECT ... FROM ...` | 取得 |
| Update | `UPDATE ... SET ...` | 更新 |
| Delete | `DELETE FROM ...` | 削除 |

頭文字をとって **CRUD（クラッド）** と呼びます。ほとんどのアプリはこの4つの組み合わせでできています。

## 5-2. 動かしてみる

```powershell
cd step05_sqlite
python sqlite_basics.py
```

```
=== 全員 ===
1 太郎 20
2 花子 25
3 次郎 18
=== 20歳以上 ===
太郎
花子
=== 更新後の太郎 ===
{'id': 1, 'name': '太郎', 'age': 21}
=== 削除後の人数: 2 ===
```

同じフォルダに `sample.db` ファイルができています。

## 5-3. コードの解説（`sqlite_basics.py`）

### 接続

```python
import sqlite3

conn = sqlite3.connect("sample.db")
conn.row_factory = sqlite3.Row
```

- `connect("ファイル名")` でデータベースに接続します。ファイルが無ければ自動で作られます。
- `conn`（connection = 接続）を通して操作します。
- `row_factory = sqlite3.Row` を設定すると、結果を `row["name"]` のように **列名で** 取り出せます（設定しないと `row[1]` のように番号でしか取れない）。

### テーブル作成

```python
conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age  INTEGER
    )
""")
```

- `"""..."""` は Python の **複数行の文字列** です。長い SQL を見やすく書けます。
- `conn.execute(SQL)` で SQL を実行します。
- `IF NOT EXISTS` … 既にテーブルがあれば何もしない（何度実行してもエラーにならない）

| 列の定義 | 意味 |
|---|---|
| `id INTEGER PRIMARY KEY AUTOINCREMENT` | 整数の ID。行を特定する番号（主キー）で、**自動で 1, 2, 3...と振られる** |
| `name TEXT NOT NULL` | 文字列。空（NULL）は禁止 |
| `age INTEGER` | 整数 |

### 追加（INSERT）と commit

```python
conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("太郎", 20))
conn.commit()
```

- `?` の部分に、後ろのタプル `("太郎", 20)` の値が順に入ります。
- **`commit()` で変更が確定** します。忘れるとファイルに保存されません。

> **重要: 値は必ず `?` で渡す**
> ```python
> # ✗ 絶対ダメ: 文字列を直接つなげる
> conn.execute(f"INSERT INTO users (name) VALUES ('{name}')")
> # ○ 正しい: ? を使う
> conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
> ```
> 直接つなげると、入力値に SQL の一部を仕込まれて任意の操作をされる「**SQL インジェクション**」という攻撃を受けます。

> **タプルの注意**: 値が1つのときは `(name,)` と **カンマが必要** です。`(name)` だとただのカッコになります。

### 取得（SELECT）

```python
rows = conn.execute("SELECT id, name, age FROM users ORDER BY id").fetchall()
for row in rows:
    print(row["id"], row["name"], row["age"])
```

- `SELECT 列名 FROM テーブル` で取得。`*` と書くと全列。
- `ORDER BY id` … id の順に並べる（`DESC` を付けると逆順）
- `WHERE age >= ?` … 条件に合う行だけ
- `.fetchall()` … 結果を **すべて** リストで受け取る
- `.fetchone()` … 結果を **1件だけ** 受け取る（無ければ `None`）

### 更新（UPDATE）・削除（DELETE）

```python
conn.execute("UPDATE users SET age = ? WHERE name = ?", (21, "太郎"))
conn.execute("DELETE FROM users WHERE name = ?", ("次郎",))
conn.commit()
```

> **注意:** `WHERE` を付け忘れると **全行** が更新・削除されます！

### 閉じる

```python
conn.close()
```

使い終わったら接続を閉じます。

## 5-4. 練習問題

1. `users` に自分の名前と年齢を追加して表示してみよう
2. 25歳以上の人だけを、年齢の高い順に表示してみよう（ヒント: `WHERE` と `ORDER BY age DESC`）

> データベースの中身を GUI で見たいときは、無料ツールの「DB Browser for SQLite」が便利です（必須ではありません）。

## まとめ

- SQLite = ファイル1つのデータベース。`import sqlite3` で使える
- 接続 → `execute(SQL, 値)` → `commit()` → `close()` が基本の流れ
- CRUD = INSERT / SELECT / UPDATE / DELETE
- 値は必ず `?` で渡す

➡ 次は [第6章 ToDo アプリを完成させる](06_ToDoアプリを完成させる.md)
