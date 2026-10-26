# pytest が自動で読み込む「テストの準備」用ファイル（SQLModel 版）
# 第11章との違い: 差し替える対象が DB_NAME から engine に変わっただけ。
#                 test_main.py は第11章から1行も変えていない

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine

import database
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """テスト専用の空のデータベースを使う TestClient を用意する"""
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    monkeypatch.setattr(database, "engine", test_engine)

    with TestClient(app) as test_client:
        yield test_client

    test_engine.dispose()   # 後片付け: エンジンが持っている接続を閉じる
