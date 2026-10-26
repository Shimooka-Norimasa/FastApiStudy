# 第1章 Python の基本（FastAPI を読むための最低限）

## この章のねらい

- この後の章のコードを読むのに必要な Python の文法だけを押さえる
- 特に FastAPI で重要な **型ヒント** と **デコレータ** を理解する

## この章が終わるとできること

- 変数・リスト・辞書・if・for・関数を読み書きできる
- `def hello(name: str) -> str:` のような型ヒント付きの関数が読める
- `@app.get("/")` のような **デコレータ** が何をしているのかイメージできる
- `with` 文の意味がわかる

---

## 1-1. 動かしてみる

```powershell
cd step01_python
python basics.py
```

結果がずらっと表示されれば OK です。以下、`basics.py` の中身を順に説明します。

## 1-2. 変数と型

```python
name = "太郎"        # 文字列 (str)
age = 20             # 整数 (int)
height = 170.5       # 小数 (float)
is_student = True    # 真偽値 (bool)
```

- `=` で変数に値を入れます。型を宣言する必要はありません。
- `#` から行末まではコメント（プログラムとしては無視される）です。
- 真偽値は `True` / `False`（先頭が大文字）。

### f文字列

```python
print(f"名前: {name}, 年齢: {age}")
# → 名前: 太郎, 年齢: 20
```

文字列の前に `f` を付けると、`{ }` の中に変数や式を埋め込めます。とてもよく使います。

## 1-3. リストと辞書

```python
fruits = ["りんご", "みかん", "ぶどう"]   # リスト
fruits.append("もも")                     # 末尾に追加
print(fruits[0])                          # → りんご（番号は 0 から）

user = {"name": "花子", "age": 25}        # 辞書
print(user["name"])                       # → 花子
user["email"] = "hanako@example.com"      # キーを追加
```

| | リスト `[ ]` | 辞書 `{ }` |
|---|---|---|
| 中身 | 値の並び | 「キー: 値」の組 |
| 取り出し方 | 番号 `fruits[0]` | キー `user["name"]` |
| 使いどころ | 一覧データ | 1件のデータの項目 |

FastAPI では **辞書を return すると JSON として返される** ので、辞書は特に重要です。

## 1-4. if 文と for 文 ― インデントが大事

```python
if age >= 20:
    print("成人です")
else:
    print("未成年です")

for fruit in fruits:
    print(f"- {fruit}")
```

- 行末の `:` の次の行から、**字下げ（スペース4つ）された部分** がブロックになります。
- 他の言語の `{ }` の代わりにインデントを使うのが Python の特徴です。字下げがずれるとエラーになります。

```python
for i, fruit in enumerate(fruits):
    print(i, fruit)   # 0 りんご / 1 みかん / ...
```

`enumerate` を使うと番号と値を同時に取り出せます。

## 1-5. 関数と型ヒント

```python
def greet(name: str, polite: bool = False) -> str:
    if polite:
        return f"{name}様、こんにちは"
    return f"{name}さん、こんにちは"

greet("太郎")                 # → 太郎さん、こんにちは
greet("花子", polite=True)    # → 花子様、こんにちは
```

| 書き方 | 意味 |
|---|---|
| `def greet(...):` | `greet` という名前の関数を定義 |
| `name: str` | 引数 `name` は文字列のつもり（**型ヒント**） |
| `polite: bool = False` | 省略したら `False` になる引数（**デフォルト値**） |
| `-> str` | 戻り値は文字列のつもり |
| `return` | 関数の結果を返す |
| `polite=True` | 引数名を指定して渡す（**キーワード引数**） |

### 型ヒントはなぜ大事？

Python 自体は型ヒントを **チェックしません**（`greet(123)` と書いても動いてしまう）。
しかし **FastAPI は型ヒントを読み取って、送られてきたデータを自動でチェック・変換** してくれます。
たとえば `number: int` と書けば、URL で `abc` が来たときに FastAPI が自動でエラーを返します（第2章で体験します）。

## 1-6. デコレータ（`@` で始まる行）

FastAPI のコードはこんな形をしています。

```python
@app.get("/")
def index():
    return {"message": "Hello"}
```

この `@app.get("/")` が **デコレータ** です。
デコレータは「直後の関数に何か処理を付け加える仕組み」で、ここでは
**「URL `/` にアクセスが来たら `index` 関数を呼ぶ」という登録** をしています。

`basics.py` では仕組みがわかるように、自作の超簡易版を作っています。

```python
routes = {}   # URL と 関数 の対応表

def route(path: str):
    def register(func):
        routes[path] = func   # 対応表に登録するだけ
        return func
    return register

@route("/hello")
def hello():
    return "Hello!"
```

`@route("/hello")` と書くと、`routes` 辞書に `{"/hello": hello関数}` が登録されます。
後から `routes["/hello"]()` で呼び出せます。

```
@route("/hello")          対応表 routes
def hello(): ...    ──▶   "/hello" → hello
                          "/bye"   → bye
```

Web フレームワークは、ブラウザから来た URL を見て、この対応表から関数を探して呼んでいる ―― というのが基本的なイメージです。
**デコレータの中身を自分で書けなくても大丈夫** です。「`@` は関数を登録している」と読めれば十分です。

## 1-7. with 文

```python
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("...")
# ここに来た時点でファイルは自動で閉じられている
```

`with` は **「使い終わったら自動で後片付けをする」** 書き方です。ファイルなど、開いたら閉じる必要があるものに使います。

## 1-8. import

```python
import sqlite3                           # モジュール全体を読み込む → sqlite3.connect(...)
from fastapi import FastAPI, Request     # モジュールの中の特定のものだけ読み込む → FastAPI()
```

他のファイルやライブラリの機能を使うときは `import` します。
自分で作った `database.py` も `import database` で読み込めます（第6章）。

## まとめ

- リスト `[ ]` と辞書 `{ }`、インデントでブロックを表す
- **型ヒント** `name: str` は FastAPI が入力チェックに使う
- **デコレータ** `@app.get("/")` は「この URL ならこの関数」という登録
- `with` は自動で後片付けしてくれる

➡ 次は [第2章 FastAPI はじめの一歩](02_FastAPIはじめの一歩.md)
