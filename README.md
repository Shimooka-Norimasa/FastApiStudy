# FastAPI + Jinja2 + SQLite 段階学習教材

Python の Web フレームワーク **FastAPI** と、テンプレートエンジン **Jinja2**、データベース **SQLite** を使って、
「ブラウザから読み書きできる ToDo アプリ」を作るまでを段階的に学ぶ教材です。

各章で **必ず動くもの** を作り、少しずつ機能を足していきます。

## 完成イメージ

```
┌────────────────────────────────┐
│ ToDo リスト                     │
│ [やることを入力      ] [追加]   │
│ ┌────────────────────────────┐ │
│ │ 牛乳を買う      [完了][削除] │ │
│ │ ~~勉強する~~    [戻す][削除] │ │
│ └────────────────────────────┘ │
└────────────────────────────────┘
```

## 目次

教材は **基本編**（第0〜6章）と **応用編**（第7〜13章）に分かれています。
基本編で ToDo アプリを完成させ、応用編でそのアプリを1章ずつ改良していきます。

### 基本編 ― FastAPI + Jinja2 + SQLite で動かす

| 章 | 資料 | サンプルコード | 内容 |
|---|---|---|---|
| 第0章 | [準備](docs/00_準備.md) | — | 仮想環境とライブラリのインストール |
| 第1章 | [Python の基本](docs/01_Pythonの基本.md) | `step01_python/` | FastAPI を読むのに必要な Python 文法 |
| 第2章 | [FastAPI はじめの一歩](docs/02_FastAPIはじめの一歩.md) | `step02_fastapi/` | Web サーバーを起動して JSON を返す |
| 第3章 | [Jinja2 で HTML を返す](docs/03_Jinja2でHTMLを返す.md) | `step03_jinja2/` | テンプレートで HTML 画面を作る |
| 第4章 | [フォームでデータを送る](docs/04_フォームでデータを送る.md) | `step04_form/` | 入力フォームと POST（保存はメモリ） |
| 第5章 | [SQLite の基本](docs/05_SQLiteの基本.md) | `step05_sqlite/` | Python 単体で SQLite を読み書き |
| 第6章 | [ToDo アプリを完成させる](docs/06_ToDoアプリを完成させる.md) | `step06_todo_app/` | ここまでを組み合わせて完成 |

### 応用編（第7〜13章） ― 実践的なアプリに育てる

| 章 | 資料 | サンプルコード | 内容 |
|---|---|---|---|
| 第7章 | [入力チェックとエラー表示](docs/07_入力チェックとエラー表示.md) | `step07_validation/` | 不正な入力を弾く、`HTTPException` で 404、HTML のエラー画面 |
| 第8章 | [Depends（依存性注入）](docs/08_Depends依存性注入.md) | `step08_depends/` | データベース接続を引数で受け取る、存在チェックの部品化 |
| 第9章 | [Pydantic で JSON API を作る](docs/09_PydanticでJSON_APIを作る.md) | `step09_json_api/` | データの形を定義し、GET/POST/PATCH/DELETE の API を作る |
| 第10章 | [JavaScript から API を使う](docs/10_JavaScriptからAPIを使う.md) | `step10_javascript/` | `fetch` でページを再読み込みせずに更新する |
| 第11章 | [テストを書く](docs/11_テストを書く.md) | `step11_test/` | `pytest` と `TestClient` で自動テスト |
| 第12章 | [SQLModel でデータベースを扱う](docs/12_SQLModelでデータベースを扱う.md) | `step12_sqlmodel/` | ORM で SQL を書かずに操作。テストで書き換えを確認 |
| 第13章 | [ワーカーで時間のかかる処理を行う](docs/13_ワーカーで時間のかかる処理を行う.md) | `step13_worker/` | キューとワーカーを自作し、CSV 書き出しを裏で実行。フレームワークはコラムで紹介 |

応用編の第11章以降では追加のライブラリを使います（各章でインストール方法を説明しています）。
まとめて入れる場合は `pip install -r requirements-advanced.txt` を実行してください。

### 付録

| 資料 | 内容 |
|---|---|
| [次のステップ・困ったとき](docs/付録.md) | よくあるエラー、用語集、さらに学ぶこと |
| [Python のインストール](docs/付録_Pythonのインストール.md) | Python がまだ入っていない人向け |

> Python がまだ入っていない場合は、先に [付録 Python のインストール](docs/付録_Pythonのインストール.md) を済ませてください。

## 教材の置き場所

この教材は **`C:\FastApiStudy`** に置いて使う前提で書かれています（置き方は [第0章 準備](docs/00_準備.md) を参照）。

## すぐに完成版を動かしたい場合

```powershell
cd C:\FastApiStudy
python -m venv .venv
C:\FastApiStudy\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd C:\FastApiStudy\step06_todo_app
uvicorn main:app --reload
```

ブラウザで http://127.0.0.1:8000 を開きます。

## 動作確認環境

- Python 3.12
- FastAPI 0.162 / Jinja2 3.1 / uvicorn 0.54 / python-multipart 0.0.32
- （応用編）pytest 9.1 / httpx2 2.16 / SQLModel 0.0.48
