# 第10章 JavaScript から API を使う

## この章のねらい

- 第9章で作った JSON API を、ブラウザの **JavaScript** から呼び出す
- 「サーバーが HTML を作る方式」と「ブラウザが画面を作る方式」の違いを知る

## この章が終わるとできること

- `fetch` で API にリクエストを送り、結果の JSON を受け取れる
- 受け取ったデータから、JavaScript で画面（HTML の要素）を作れる
- ページの再読み込みなしで、追加・完了・削除ができる ToDo アプリが作れる

---

## 10-1. 2つの方式の違い

これまでの方式では、ボタンを押すたびに **ページ全体を読み込み直して** いました。

```
【これまで: サーバーで HTML を作る（Jinja2）】
 ボタン → POST /add → リダイレクト → GET / → サーバーが HTML を丸ごと作る → 画面全体を表示し直す

【この章: ブラウザで画面を作る（JavaScript）】
 ボタン → JavaScript が POST /api/todos → JSON を受け取る → JavaScript が一覧の部分だけを書き換える
```

| | サーバーで HTML を作る | ブラウザで画面を作る |
|---|---|---|
| 画面を作る担当 | Python（Jinja2） | JavaScript |
| サーバーが返すもの | HTML | JSON |
| 操作のたびに | ページ全体を読み込み直す | 必要な部分だけ書き換える |
| 良いところ | シンプル。JavaScript が要らない | 操作がなめらか |

どちらが正解というわけではありません。シンプルな管理画面などでは今でも前者がよく使われます。

> この章ではじめて JavaScript を使います。JavaScript はブラウザの中で動くプログラミング言語です。
> 文法は Python と違うところが多いですが、ここではコードの流れがわかれば十分です。

## 10-2. ファイル構成

```
step10_javascript/
├── main.py            … 画面の入れ物と API だけを返す（フォーム用の URL は削除）
├── api.py / schemas.py / dependencies.py / database.py   … 第9章と同じ
├── templates/
│   ├── base.html      … 第9章と同じ
│   ├── error.html     … 第9章と同じ
│   └── index.html     … 一覧の「入れ物」だけ
└── static/
    ├── style.css
    └── app.js         … 画面を動かす JavaScript（新規）
```

**API 側（`api.py` など）は1行も変えていません。** 第9章で API を用意しておいたので、画面だけを作り替えられました。

## 10-3. サーバー側（`main.py`）

```python
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"max_length": MAX_TITLE_LENGTH})
```

ToDo の一覧はもう渡していません。画面の「入れ物」だけを返し、中身は JavaScript が API から取得します。
`/add`、`/toggle/...`、`/delete/...` の URL は不要になったので削除しました。

## 10-4. 画面の入れ物（`templates/index.html`）

```html
<p id="error" class="error" hidden></p>

<form id="add-form" class="add-form">
    <input type="text" id="title" placeholder="やることを入力" maxlength="{{ max_length }}">
    <button type="submit">追加</button>
</form>

<ul id="todo-list" class="todo-list"></ul>

<script src="{{ url_for('static', path='app.js') }}" defer></script>
```

- `id="..."` … JavaScript から部品を探すための名前
- `hidden` … 最初は隠しておく
- `<form>` に `action` と `method` がない … 送信は JavaScript が受け持つため
- `<ul>` は空っぽ … 中身は JavaScript が作る
- `<script src="..." defer>` … JavaScript ファイルを読み込む。`defer` を付けると、HTML を最後まで読み込んでから実行される

## 10-5. JavaScript（`static/app.js`）

### Python との書き方の違い

| | Python | JavaScript |
|---|---|---|
| 変数 | `x = 1` | `const x = 1;`（変えない）/ `let x = 1;`（変える） |
| 関数 | `def f(a):` | `function f(a) { }` |
| ブロック | インデント | `{ }` |
| 文の終わり | 改行 | `;`（省略可能なことも多い） |
| 真偽値 | `True` / `False` | `true` / `false` |
| 辞書 | `{"a": 1}` | `{ a: 1 }`（オブジェクト） |
| 否定 | `not x` | `!x` |
| 等しい | `==` | `===` |
| 埋め込み文字列 | `f"id={x}"` | `` `id=${x}` ``（バッククォート） |
| コメント | `# ...` | `// ...` |

### 部品を取り出す

```javascript
const form = document.getElementById("add-form");
const list = document.getElementById("todo-list");
```

`document` は表示中のページ全体を表し、`getElementById` で `id` を指定して HTML の部品（要素）を取り出します。

### API を呼ぶ: `fetch`

```javascript
async function callApi(method, url, body) {
  const options = { method: method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const data = await response.json();
    throw new Error(toMessage(data.detail));
  }
  if (response.status === 204) {
    return null;
  }
  return await response.json();
}
```

| 部分 | 説明 |
|---|---|
| `fetch(url, options)` | ブラウザの機能で、URL にリクエストを送る |
| `"Content-Type": "application/json"` | 「本体は JSON です」とサーバーに伝える |
| `JSON.stringify(body)` | JavaScript のオブジェクトを JSON の文字列に変換する |
| `response.ok` | ステータスコードが 200番台なら `true` |
| `response.json()` | 返ってきた JSON を JavaScript のオブジェクトに変換する |
| `throw new Error(...)` | エラーを投げる（Python の `raise` にあたる） |

#### `async` / `await` とは

通信には時間がかかります。`await` は「**結果が返ってくるまで待ってから次の行へ進む**」という意味です。
`await` を使う関数には `async` を付けます。

```javascript
const response = await fetch(url);   // 通信が終わるまで待つ
const data = await response.json();  // JSON への変換が終わるまで待つ
```

### 画面を作る

```javascript
function render(todos) {
  list.replaceChildren(); // いったん空にする

  for (const todo of todos) {
    const li = document.createElement("li");

    const title = document.createElement("span");
    title.className = "title";
    title.textContent = todo.title;

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "削除";
    deleteButton.addEventListener("click", () => deleteTodo(todo));

    li.append(title, deleteButton);
    list.append(li);
  }
}
```

（実際のコードでは「完了」ボタンや「やることはありません」の表示もあります）

| 部分 | 説明 |
|---|---|
| `document.createElement("li")` | `<li>` 要素を新しく作る |
| `title.textContent = ...` | 要素の中の文字を設定する |
| `li.className = "done"` | `class="done"` を設定する |
| `addEventListener("click", 関数)` | クリックされたら関数を呼ぶ |
| `() => deleteTodo(todo)` | 「`deleteTodo(todo)` を呼ぶ関数」を1行で書いたもの（アロー関数） |
| `list.append(li)` | 一覧の中に追加する |

> **`textContent` を使う理由（XSS 対策）**
> `innerHTML` を使うと、文字列を HTML として解釈してしまいます。
> もし ToDo のタイトルに `<img src=x onerror=alert(1)>` のような文字が入っていると、それが実行されてしまいます（XSS）。
> `textContent` は文字をそのまま表示するので安全です。第3章で Jinja2 が自動でやってくれていたことを、JavaScript では自分で気をつける必要があります。

### 操作

```javascript
async function addTodo(event) {
  event.preventDefault(); // フォーム送信でページが再読み込みされるのを止める
  try {
    await callApi("POST", "/api/todos", { title: titleInput.value });
    titleInput.value = "";
    showError("");
    await loadTodos();
  } catch (error) {
    showError(error.message);
  }
}
```

- `event.preventDefault()` … フォームはそのままだとページを読み込み直してしまうので、それを止めます
- `try { } catch (error) { }` … `try` の中でエラーが起きたら `catch` の中が実行されます（Python の `try` / `except` にあたる）
- 追加に成功したら入力欄を空にし、一覧を取得し直して表示します

完了の切り替えと削除も同じ流れです。

```javascript
await callApi("PATCH", `/api/todos/${todo.id}`, { done: !todo.done });
await callApi("DELETE", `/api/todos/${todo.id}`);
```

### 起動時

```javascript
form.addEventListener("submit", addTodo); // 「追加」が押されたら addTodo を呼ぶ
loadTodos();                              // 最初の一覧表示
```

## 10-6. 動かしてみる

```powershell
cd C:\FastApiStudy\step10_javascript
uvicorn main:app --reload
```

http://127.0.0.1:8000 を開き、追加・完了・削除をしてみてください。
見た目は同じですが、**ページの再読み込みが起きていない** ことに注目してください（ブラウザのタブのくるくるが出ない）。

### 開発者ツールで通信を見る

ブラウザで **F12** キーを押すと開発者ツールが開きます。

- **Network（ネットワーク）タブ** … ボタンを押したときに送られた API リクエストと、返ってきた JSON を確認できる
- **Console（コンソール）タブ** … JavaScript のエラーが表示される。動かないときはまずここを見る

## 10-7. 練習問題

1. 一覧の上に「全 ○ 件（未完了 ○ 件）」と表示してみよう
   - ヒント: `todos.length` で件数、`todos.filter((t) => !t.done).length` で未完了の件数
2. 削除ボタンを押したときに「本当に削除しますか？」と確認するようにしてみよう
   - ヒント: `if (!confirm("本当に削除しますか？")) { return; }`

## まとめ

- `fetch` で API を呼び、`await` で結果を待つ
- JSON を受け取って、`createElement` と `textContent` で画面を作る
- 画面を作る担当が JavaScript に移ったので、サーバーは API と入れ物だけを返せばよい
- API を先に作っておいたので、API 側を変えずに画面だけ作り替えられた

➡ 次は [第11章 テストを書く](11_テストを書く.md)
