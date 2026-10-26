# pytest が自動で読み込む「テストの準備」用ファイル
# 第12章との違い: CSV の書き出し先と待ち時間も、テスト用に差し替える

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine

import database
import tasks
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """テスト専用の空のデータベースを使う TestClient を用意する"""
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    monkeypatch.setattr(database, "engine", test_engine)

    # CSV は一時フォルダに書き出し、テストが遅くならないよう待ち時間は 0 秒にする
    monkeypatch.setattr(tasks, "EXPORT_DIR", str(tmp_path / "exports"))
    monkeypatch.setattr(tasks, "WAIT_SECONDS", 0)

    with TestClient(app) as test_client:
        yield test_client

    test_engine.dispose()   # 後片付け: エンジンが持っている接続を閉じる
