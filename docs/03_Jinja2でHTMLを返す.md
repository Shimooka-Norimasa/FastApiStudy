# 第3章 Jinja2 で HTML を返す

## この章のねらい

- JSON ではなく、人が見るための **HTML 画面** を返す
- **テンプレートエンジン（Jinja2）** の考え方と基本文法を理解する

## この章が終わるとできること

- Python から渡した値を HTML に埋め込んで表示できる
- テンプレート内で `if`（条件分岐）と `for`（くり返し）が使える
- 共通部分（ヘッダーなど）を親テンプレートにまとめ、複数ページで使い回せる

---

## 3-1. テンプレートエンジンとは

第2章では JSON を返しましたが、普通の Web サイトでは HTML を返します。
しかし、Python の文字列で HTML を組み立てるのは大変です。

```python
# こう書くのはつらい…
return "<html><body><h1>ようこそ、" + user_name + "さん</h1>...</body></html>"
```

そこで、**HTML の「ひな形（テンプレート）」を別ファイルに用意しておき、変わる部分だけを後から埋め込む** 方法を使います。
この埋め込みをしてくれる道具が **テンプレートエンジン** で、Python では **Jinja2（ジンジャ）** が定番です。

```
 テンプレート (index.html)          Python から渡す値           できあがる HTML
 ┌──────────────────────┐      ┌─────────────────────┐     ┌──────────────────────┐
 │<p>ようこそ、           │  +   │ user_name = "太郎"  │ ──▶ │<p>ようこそ、          │
 │   {{ user_name }}さん</p>│      └─────────────────────┘     │   太郎さん</p>         │
 └──────────────────────┘                                    └──────────────────────┘
```

役割分担:

- **Python（main.py）** … データを用意する
- **テンプレート（.html）** … 見た目を決める

## 3-2. フォルダ構成

```
step03_jinja2/
├── main.py
└── templates/        ← テンプレートはここに置く
    ├── base.html     … 共通の土台（親）
    ├── index.html    … トップページ（子）
    └── hello.html    … あいさつページ（子）
```

## 3-3. Python 側（`main.py`）

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    fruits = ["りんご", "みかん", "ぶどう"]
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "Jinja2 のテスト", "user_name": "太郎", "fruits": fruits},
    )
```

| 部分 | 説明 |
|---|---|
| `Jinja2Templates(directory="templates")` | `templates` フォルダのファイルをテンプレートとして使う設定 |
| `response_class=HTMLResponse` | この URL は HTML を返す、と明示（`/docs` の表示が正しくなる） |
| `request: Request` | ブラウザからのリクエスト情報。**テンプレートを使うときは必ず受け取って渡す** |
| `TemplateResponse(request, "index.html", {...})` | テンプレートに値を埋め込んで HTML を返す |
| `{"title": ..., "user_name": ...}` | テンプレートに渡す値。**キー名がテンプレート内の変数名** になる |

## 3-4. Jinja2 の基本文法

Jinja2 の書き方は3種類だけ覚えれば十分です。

| 書き方 | 意味 | 例 |
|---|---|---|
| `{{ ... }}` | 値を **表示** する | `{{ user_name }}` |
| `{% ... %}` | **処理**（if, for など）を書く | `{% for x in list %}` |
| `{# ... #}` | **コメント**（HTML に出力されない） | `{# メモ #}` |

### 値の表示

```html
<h1>{{ title }}</h1>
<p>ようこそ、{{ user_name }} さん</p>
```

### 条件分岐（if）

```html
{% if fruits %}
    <p>果物は {{ fruits | length }} 個あります</p>
{% else %}
    <p>果物はありません</p>
{% endif %}
```

- Python と違い、インデントではなく **`{% endif %}` でブロックを閉じます**。
- `fruits | length` の `|` は **フィルター** といい、値を加工します。`length` は要素数を返します。

### くり返し（for）

```html
<ul>
{% for fruit in fruits %}
    <li>{{ loop.index }}. {{ fruit }}</li>
{% endfor %}
</ul>
```

- `loop.index` は for の中で使える特別な変数で、1, 2, 3... と回数が入ります。

結果:

```html
<ul>
    <li>1. りんご</li>
    <li>2. みかん</li>
    <li>3. ぶどう</li>
</ul>
```

## 3-5. テンプレートの継承（共通部分をまとめる）

ページが増えると、`<head>` やヘッダーなどを毎回書くのは面倒です。
そこで **親テンプレート** に共通部分を書き、**子テンプレート** は違う部分だけを書きます。

**親: `base.html`**

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}サンプル{% endblock %}</title>
</head>
<body>
    <header>
        <a href="/">トップ</a> | <a href="/hello/花子">あいさつ</a>
    </header>
    <hr>
    {% block content %}{% endblock %}
</body>
</html>
```

**子: `hello.html`**

```html
{% extends "base.html" %}

{% block title %}あいさつ{% endblock %}

{% block content %}
    <h1>こんにちは、{{ name }} さん！</h1>
{% endblock %}
```

- `{% extends "base.html" %}` … 「base.html を土台にする」
- `{% block 名前 %}...{% endblock %}` … 親の同じ名前の block を、子の中身で **差し替え** る

```
 base.html                    hello.html
 ┌──────────────────┐         ┌─────────────────────┐
 │ <head>...        │         │ block title         │
 │ block title  ◀───┼─────────┤   「あいさつ」       │
 │ <header>...      │         │ block content       │
 │ block content ◀──┼─────────┤   <h1>こんにちは…    │
 └──────────────────┘         └─────────────────────┘
```

## 3-6. 動かしてみる

```powershell
cd step03_jinja2
uvicorn main:app --reload
```

- http://127.0.0.1:8000 → 果物の一覧が表示される
- http://127.0.0.1:8000/hello/taro → 「こんにちは、taro さん！」
- ブラウザで右クリック →「ページのソースを表示」で、テンプレートから作られた HTML を確認してみましょう

> **補足: 自動エスケープ**
> `{{ }}` で表示する値に `<script>` などが含まれていても、Jinja2 は自動で `&lt;script&gt;` のように変換（エスケープ）します。
> これにより、入力された文字列が HTML として実行される攻撃（XSS）を防げます。

## 3-7. 練習問題

1. `main.py` の `fruits` を空のリスト `[]` にすると、表示がどう変わるか確認しよう
2. `/profile` にアクセスすると、名前と年齢を表示する新しいページ（`profile.html`）を作ってみよう。`base.html` を継承すること

## まとめ

- テンプレートエンジン = HTML のひな形に値を埋め込む道具
- `{{ 値 }}` で表示、`{% if %}` `{% for %}` で処理、`{% end〇〇 %}` で閉じる
- `TemplateResponse(request, "ファイル名", {値の辞書})` で HTML を返す
- `extends` と `block` で共通部分を使い回す

➡ 次は [第4章 フォームでデータを送る](04_フォームでデータを送る.md)
