# 第11章: テスト
# 実行方法（step11_test フォルダで）:  pytest -v
#
# pytest は「test_ で始まるファイル」の「test_ で始まる関数」を自動で探して実行する
# 引数に client と書くと、conftest.py の client フィクスチャが渡される

import pytest


# ---------- 画面 ----------

def test_トップページが表示される(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "ToDo リスト" in response.text


def test_存在しないページはHTMLのエラー画面になる(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert "エラー 404" in response.text


# ---------- API: 追加と取得 ----------

def test_最初は一覧が空(client):
    response = client.get("/api/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_追加できる(client):
    response = client.post("/api/todos", json={"title": "牛乳を買う"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "牛乳を買う", "done": False}


def test_前後の空白は取り除かれる(client):
    response = client.post("/api/todos", json={"title": "  勉強する  "})
    assert response.json()["title"] == "勉強する"


# parametrize: 同じテストを、値を変えて何回も実行する
@pytest.mark.parametrize("title", ["", "   ", "あ" * 101])
def test_不正なタイトルは追加できない(client, title):
    response = client.post("/api/todos", json={"title": title})
    assert response.status_code == 422
    assert client.get("/api/todos").json() == []   # 何も追加されていない


def test_100文字ちょうどは追加できる(client):
    response = client.post("/api/todos", json={"title": "あ" * 100})
    assert response.status_code == 201


def test_一覧は新しい順に並ぶ(client):
    client.post("/api/todos", json={"title": "1つ目"})
    client.post("/api/todos", json={"title": "2つ目"})

    titles = [todo["title"] for todo in client.get("/api/todos").json()]
    assert titles == ["2つ目", "1つ目"]


def test_1件取得できる(client):
    client.post("/api/todos", json={"title": "牛乳を買う"})

    response = client.get("/api/todos/1")
    assert response.status_code == 200
    assert response.json()["title"] == "牛乳を買う"


def test_存在しないToDoは404(client):
    response = client.get("/api/todos/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "指定された ToDo が見つかりません"}


# ---------- API: 更新と削除 ----------

def test_完了にできる(client):
    client.post("/api/todos", json={"title": "牛乳を買う"})

    response = client.patch("/api/todos/1", json={"done": True})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "牛乳を買う", "done": True}


def test_タイトルだけ変更すると完了状態はそのまま(client):
    client.post("/api/todos", json={"title": "牛乳を買う"})
    client.patch("/api/todos/1", json={"done": True})

    response = client.patch("/api/todos/1", json={"title": "牛乳を2本買う"})
    assert response.json() == {"id": 1, "title": "牛乳を2本買う", "done": True}


def test_削除できる(client):
    client.post("/api/todos", json={"title": "牛乳を買う"})

    response = client.delete("/api/todos/1")
    assert response.status_code == 204
    assert client.get("/api/todos/1").status_code == 404


def test_存在しないToDoは削除できない(client):
    response = client.delete("/api/todos/999")
    assert response.status_code == 404
