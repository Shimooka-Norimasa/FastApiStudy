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

| 章 | 資料 | サンプルコード | 内容 |
|---|---|---|---|
| 第0章 | [準備](docs/00_準備.md) | — | 仮想環境とライブラリのインストール |
| 第1章 | [Python の基本](docs/01_Pythonの基本.md) | `step01_python/` | FastAPI を読むのに必要な Python 文法 |
| 第2章 | [FastAPI はじめの一歩](docs/02_FastAPIはじめの一歩.md) | `step02_fastapi/` | Web サーバーを起動して JSON を返す |
| 第3章 | [Jinja2 で HTML を返す](docs/03_Jinja2でHTMLを返す.md) | `step03_jinja2/` | テンプレートで HTML 画面を作る |
| 第4章 | [フォームでデータを送る](docs/04_フォームでデータを送る.md) | `step04_form/` | 入力フォームと POST（保存はメモリ） |
| 第5章 | [SQLite の基本](docs/05_SQLiteの基本.md) | `step05_sqlite/` | Python 単体で SQLite を読み書き |
| 第6章 | [ToDo アプリを完成させる](docs/06_ToDoアプリを完成させる.md) | `step06_todo_app/` | ここまでを組み合わせて完成 |
| 付録 | [次のステップ・困ったとき](docs/付録.md) | — | よくあるエラーと発展学習 |

## すぐに完成版を動かしたい場合

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd step06_todo_app
uvicorn main:app --reload
```

ブラウザで http://127.0.0.1:8000 を開きます。

## 動作確認環境

- Python 3.12
- FastAPI 0.162 / Jinja2 3.1 / uvicorn 0.54 / python-multipart 0.0.32
