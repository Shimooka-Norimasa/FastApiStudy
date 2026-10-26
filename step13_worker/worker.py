# 第13章: 自作ワーカー
# 実行方法（step13_worker フォルダで、uvicorn とは別のターミナルで）:  python worker.py
# 止めるときは Ctrl + C
#
# やっていること:
#   1. jobs テーブルから「待ち」の仕事を1件取り出す
#   2. 仕事を実行し、結果（完了 / 失敗）を jobs テーブルに書き込む
#   3. 仕事が無ければ少し待って、また 1 に戻る（これをずっとくり返す）

import time

from sqlmodel import Session

import database
import tasks

POLL_SECONDS = 1   # 仕事が無いときに、次に確認するまで待つ秒数


def process_one_job() -> bool:
    """仕事を1件処理する。処理した仕事があれば True、無ければ False を返す"""
    # database.engine と書く（from database import engine としない）のは、
    # テストのときに engine をテスト用のものへ差し替えられるようにするため
    with Session(database.engine) as session:
        job = database.claim_next_job(session)
        if job is None:
            return False

        print(f"仕事 {job.id} を開始します")
        try:
            result_file = tasks.export_todos_csv(session, job.id)
        except Exception as error:
            # 処理の途中でどんなエラーが起きても、ワーカー自体は止めずに「失敗」として記録する
            database.fail_job(session, job, str(error))
            print(f"仕事 {job.id} は失敗しました: {error}")
        else:
            # try の中でエラーが起きなかったときだけ、ここが実行される
            database.finish_job(session, job, result_file)
            print(f"仕事 {job.id} が完了しました: {result_file}")
        return True


def main():
    database.init_db()   # Web アプリより先に起動しても困らないよう、テーブルを準備しておく

    with Session(database.engine) as session:
        count = database.requeue_running_jobs(session)
        if count:
            print(f"途中で止まっていた仕事 {count} 件を、待ちに戻しました")

    print("ワーカーを起動しました（止めるときは Ctrl + C）")
    try:
        while True:
            if not process_one_job():
                time.sleep(POLL_SECONDS)   # 仕事が無かったので少し待つ
    except KeyboardInterrupt:
        # Ctrl + C を押すと KeyboardInterrupt という例外が起きる
        print("ワーカーを止めました")


# このファイルを python worker.py で直接実行したときだけ main() を呼ぶ
# （テストなどで import されたときは呼ばれない）
if __name__ == "__main__":
    main()
