# pytest が自動で読み込む「テストの準備」用ファイル
# ここに書いた fixture（フィクスチャ）は、すべてのテストファイルから使える

import pytest
from fastapi.testclient import TestClient

import database
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """テスト専用の空のデータベースを使う TestClient を用意する"""
    # tmp_path: pytest がテストごとに用意してくれる一時フォルダ
    # monkeypatch: テスト中だけ値を差し替え、終わったら元に戻してくれる道具
    # → 本物の todo.db を汚さず、毎回まっさらなデータベースでテストできる
    monkeypatch.setattr(database, "DB_NAME", str(tmp_path / "test.db"))

    # with で使うと、起動時の処理（lifespan の init_db）も実行される
    with TestClient(app) as test_client:
        yield test_client   # ここでテスト関数に渡す
