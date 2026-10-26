# 第13章: ワーカーのテスト
# 実行方法（C:\FastApiStudy\step13_worker で）:  pytest -v
#
# テストの中では worker.py をずっと動かすのではなく、
# process_one_job() を呼んで「仕事を1件だけ処理する」ところを確かめる

from sqlmodel import Session

import database
import tasks
import worker


def test_登録した仕事は待ちになる(client):
    response = client.post("/api/exports")
    assert response.status_code == 202
    assert response.json() == {"id": 1, "status": "pending", "error": None}


def test_ワーカーが処理すると完了になる(client):
    client.post("/api/exports")

    assert worker.process_one_job() is True
    assert client.get("/api/exports/1").json()["status"] == "done"


def test_完了したらCSVをダウンロードできる(client):
    client.post("/api/todos", json={"title": "牛乳を買う"})
    client.post("/api/todos", json={"title": "勉強する"})
    client.patch("/api/todos/2", json={"done": True})
    client.post("/api/exports")
    worker.process_one_job()

    response = client.get("/api/exports/1/download")
    assert response.status_code == 200
    # 先頭の "﻿" は utf-8-sig で書き出したときに付く印（BOM）
    assert response.text.splitlines() == [
        "﻿id,タイトル,状態",
        "1,牛乳を買う,未完了",
        "2,勉強する,完了",
    ]


def test_完了する前はダウンロードできない(client):
    client.post("/api/exports")

    response = client.get("/api/exports/1/download")
    assert response.status_code == 409


def test_仕事が無ければ何もしない(client):
    assert worker.process_one_job() is False


def test_仕事は登録した順に1件ずつ処理される(client):
    client.post("/api/exports")
    client.post("/api/exports")

    worker.process_one_job()
    assert client.get("/api/exports/1").json()["status"] == "done"
    assert client.get("/api/exports/2").json()["status"] == "pending"

    worker.process_one_job()
    assert client.get("/api/exports/2").json()["status"] == "done"


def test_処理中にエラーが起きると失敗になる(client, monkeypatch):
    def broken_export(session, job_id):
        raise RuntimeError("ディスクがいっぱいです")

    # tasks.export_todos_csv を、必ずエラーになる関数に差し替える
    monkeypatch.setattr(tasks, "export_todos_csv", broken_export)
    client.post("/api/exports")

    assert worker.process_one_job() is True   # ワーカー自体は止まらない
    assert client.get("/api/exports/1").json() == {
        "id": 1,
        "status": "failed",
        "error": "ディスクがいっぱいです",
    }


def test_実行中のまま残った仕事は待ちに戻せる(client):
    client.post("/api/exports")
    with Session(database.engine) as session:
        database.claim_next_job(session)   # 取り出した（実行中にした）ところでワーカーが止まった、という想定

        assert database.requeue_running_jobs(session) == 1

    assert client.get("/api/exports/1").json()["status"] == "pending"


def test_存在しない仕事は404(client):
    response = client.get("/api/exports/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "指定された仕事が見つかりません"}
