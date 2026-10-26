// 第10章: JSON API を呼び出して画面を書き換える JavaScript

// HTML の部品を id で取り出しておく
const form = document.getElementById("add-form");
const titleInput = document.getElementById("title");
const list = document.getElementById("todo-list");
const errorBox = document.getElementById("error");

// ---------- API を呼ぶ関数 ----------

// fetch で API にリクエストを送り、結果の JSON を返す
// async / await: 「通信が終わるまで待ってから次の行へ進む」ための書き方
async function callApi(method, url, body) {
  const options = { method: method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body); // JavaScript のオブジェクト → JSON 文字列
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    // 200番台以外はエラー。FastAPI は {"detail": ...} の形でエラー内容を返す
    const data = await response.json();
    throw new Error(toMessage(data.detail));
  }
  if (response.status === 204) {
    return null; // 204 は本体が無い
  }
  return await response.json(); // JSON 文字列 → JavaScript のオブジェクト
}

// FastAPI のエラー内容を、画面に出す文章に変える
function toMessage(detail) {
  // 入力チェックのエラー(422)は配列で返ってくる
  if (Array.isArray(detail)) {
    return "入力内容を確認してください（1〜100文字）";
  }
  return detail;
}

// ---------- 画面を描く関数 ----------

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = !message; // メッセージが空なら隠す
}

// ToDo の配列を受け取り、一覧を作り直す
function render(todos) {
  list.replaceChildren(); // いったん空にする

  if (todos.length === 0) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = "やることはありません";
    list.append(li);
    return;
  }

  for (const todo of todos) {
    const li = document.createElement("li");
    if (todo.done) {
      li.className = "done";
    }

    const title = document.createElement("span");
    title.className = "title";
    // textContent は文字をそのまま表示する（HTML として解釈しない = XSS 対策）
    title.textContent = todo.title;

    const toggleButton = document.createElement("button");
    toggleButton.textContent = todo.done ? "戻す" : "完了";
    toggleButton.addEventListener("click", () => toggleTodo(todo));

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "削除";
    deleteButton.className = "delete";
    deleteButton.addEventListener("click", () => deleteTodo(todo));

    li.append(title, toggleButton, deleteButton);
    list.append(li);
  }
}

// ---------- 操作 ----------

// 一覧を取得して表示する
async function loadTodos() {
  const todos = await callApi("GET", "/api/todos");
  render(todos);
}

// 追加
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

// 完了/未完了の切り替え
async function toggleTodo(todo) {
  try {
    await callApi("PATCH", `/api/todos/${todo.id}`, { done: !todo.done });
    showError("");
    await loadTodos();
  } catch (error) {
    showError(error.message);
  }
}

// 削除
async function deleteTodo(todo) {
  try {
    await callApi("DELETE", `/api/todos/${todo.id}`);
    showError("");
    await loadTodos();
  } catch (error) {
    showError(error.message);
  }
}

// ---------- 第13章で追加: CSV 書き出し ----------

const exportButton = document.getElementById("export-button");
const exportStatus = document.getElementById("export-status");

const STATUS_LABELS = {
  pending: "待ち（ワーカーが受け取るのを待っています）",
  running: "実行中…",
  done: "完了",
  failed: "失敗",
};

// 仕事を登録し、状態の確認を始める
async function startExport() {
  try {
    const job = await callApi("POST", "/api/exports");
    exportButton.disabled = true; // 終わるまでボタンを押せないようにする
    showError("");
    showExportStatus(job);
    setTimeout(() => checkExport(job.id), 1000);
  } catch (error) {
    showError(error.message);
  }
}

// 仕事の状態を確認する。終わっていなければ、1秒後にもう一度確認する（ポーリング）
async function checkExport(jobId) {
  try {
    const job = await callApi("GET", `/api/exports/${jobId}`);
    showExportStatus(job);
    if (job.status === "pending" || job.status === "running") {
      setTimeout(() => checkExport(jobId), 1000);
    } else {
      exportButton.disabled = false; // 完了・失敗したら、また押せるようにする
    }
  } catch (error) {
    showError(error.message);
    exportButton.disabled = false;
  }
}

// 仕事の状態を画面に表示する。完了していればダウンロードのリンクも出す
function showExportStatus(job) {
  exportStatus.replaceChildren();
  exportStatus.append(`仕事 ${job.id}: ${STATUS_LABELS[job.status]}`);

  if (job.status === "done") {
    const link = document.createElement("a");
    link.href = `/api/exports/${job.id}/download`;
    link.textContent = "ダウンロード";
    exportStatus.append(" ", link);
  }
  if (job.status === "failed") {
    exportStatus.append(`（${job.error}）`);
  }
}

// ---------- 起動時の処理 ----------

form.addEventListener("submit", addTodo); // 「追加」ボタンが押されたら addTodo を呼ぶ
exportButton.addEventListener("click", startExport); // 「CSV に書き出す」が押されたら startExport を呼ぶ
loadTodos(); // 最初の一覧表示
