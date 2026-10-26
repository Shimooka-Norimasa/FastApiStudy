# ワーカーが実行する「時間のかかる処理」を書くファイル
# Web アプリ（main.py）からは呼ばれず、ワーカー（worker.py）だけが使う

import csv
import time
from pathlib import Path

from sqlmodel import Session

import database

EXPORT_DIR = "exports"   # 書き出したファイルを置くフォルダ
WAIT_SECONDS = 5         # 重い処理のふりをするための待ち時間（秒）


def export_todos_csv(session: Session, job_id: int) -> str:
    """ToDo の一覧を CSV ファイルに書き出し、作ったファイルの名前を返す"""
    # 本物のアプリでは、ここが「大量のデータの集計」や「メール送信」などの重い処理になる
    time.sleep(WAIT_SECONDS)

    folder = Path(EXPORT_DIR)
    folder.mkdir(exist_ok=True)   # フォルダが無ければ作る
    file_name = f"todos_{job_id}.csv"

    # encoding="utf-8-sig" にすると、Excel で開いても日本語が文字化けしない
    # newline="" は csv モジュールを使うときの決まりごと（余計な空行が入るのを防ぐ）
    with open(folder / file_name, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "タイトル", "状態"])   # 見出しの行
        for todo in reversed(database.get_all_todos(session)):   # 古い順に並べる
            writer.writerow([todo.id, todo.title, "完了" if todo.done else "未完了"])

    return file_name
