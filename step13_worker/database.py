# データベース操作をまとめたファイル（SQLModel 版）
# 第12章との違い: ワーカー用の「仕事（ジョブ）」テーブル JobRow と、その操作を追加

from sqlmodel import Field, Session, SQLModel, col, create_engine, select, update

DB_URL = "sqlite:///todo.db"   # 「sqlite の todo.db ファイル」という意味の接続先

# engine: データベースへの接続を管理するオブジェクト（アプリ全体で1つ作る）
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


# テーブルの定義。クラス1つ = テーブル1つ、属性1つ = 列1つ
# table=True を付けると「データベースのテーブル」として扱われる
class TodoRow(SQLModel, table=True):
    __tablename__ = "todos"

    # 主キー。追加する時点では id が決まっていないので None を許す（保存すると自動で番号が入る）
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False   # SQLite には真偽値の型が無いが、SQLModel が 0/1 と自動で変換してくれる


def get_session():
    """リクエストごとにセッションを作り、終わったら閉じる（Depends で使う）"""
    # Session: データベースとのやり取りを1まとまりで行う単位（第8章の接続 conn にあたる）
    with Session(engine) as session:
        yield session


def init_db():
    """テーブルが無ければ作る（CREATE TABLE を自分で書く必要がない）"""
    SQLModel.metadata.create_all(engine)


def get_all_todos(session: Session) -> list[TodoRow]:
    """全件取得（新しい順）"""
    # SELECT * FROM todos ORDER BY id DESC と同じ意味
    statement = select(TodoRow).order_by(col(TodoRow.id).desc())
    return list(session.exec(statement).all())


def get_todo(session: Session, todo_id: int) -> TodoRow | None:
    """主キーで1件取得。見つからなければ None を返す"""
    return session.get(TodoRow, todo_id)


def add_todo(session: Session, title: str) -> TodoRow:
    """1件追加し、追加した ToDo を返す"""
    todo = TodoRow(title=title)
    session.add(todo)       # 追加の予約
    session.commit()        # 確定（ここで INSERT が実行される）
    session.refresh(todo)   # データベースから最新の値（自動採番された id など）を読み直す
    return todo


def update_todo(session: Session, todo: TodoRow, title: str, done: bool) -> TodoRow:
    """タイトルと完了状態を更新する"""
    todo.title = title      # 属性を書き換えて commit すると UPDATE が実行される
    todo.done = done
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def delete_todo(session: Session, todo: TodoRow):
    """1件削除"""
    session.delete(todo)
    session.commit()


# ---------- ここから第13章で追加: 仕事（ジョブ）のテーブル ----------

# 仕事の状態。文字列をそのまま書くとタイプミスに気づけないので、定数にしておく
PENDING = "pending"   # 待ち（ワーカーに取り出されるのを待っている）
RUNNING = "running"   # 実行中
DONE = "done"         # 完了
FAILED = "failed"     # 失敗


# jobs テーブル = 仕事の待ち行列（キュー）
class JobRow(SQLModel, table=True):
    __tablename__ = "jobs"

    id: int | None = Field(default=None, primary_key=True)
    status: str = PENDING
    result_file: str | None = None   # 完了したときに作られたファイルの名前
    error: str | None = None         # 失敗したときのエラーメッセージ


def add_job(session: Session) -> JobRow:
    """仕事を「待ち」の状態で登録する（Web アプリ側が使う）"""
    job = JobRow()
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_job(session: Session, job_id: int) -> JobRow | None:
    """主キーで1件取得。見つからなければ None を返す"""
    return session.get(JobRow, job_id)


def claim_next_job(session: Session) -> JobRow | None:
    """いちばん古い「待ち」の仕事を1件取り出し、「実行中」にして返す（ワーカー側が使う）"""
    while True:
        statement = (
            select(JobRow)
            .where(JobRow.status == PENDING)
            .order_by(col(JobRow.id))
            .limit(1)
        )
        job = session.exec(statement).first()
        if job is None:
            return None   # 待ちの仕事が無い

        # 「まだ待ちのままなら実行中にする」という条件付きの UPDATE
        # ワーカーを複数動かしたとき、同じ仕事を2つのワーカーが取ってしまうのを防ぐ
        result = session.exec(
            update(JobRow)
            .where(col(JobRow.id) == job.id, col(JobRow.status) == PENDING)
            .values(status=RUNNING)
        )
        session.commit()
        if result.rowcount == 1:   # 書き換えられた行が1行 = 自分が取れた
            session.refresh(job)
            return job
        # 0行 = 一瞬の差で他のワーカーに取られた。次の仕事を探し直す


def finish_job(session: Session, job: JobRow, result_file: str):
    """仕事を「完了」にする"""
    job.status = DONE
    job.result_file = result_file
    session.add(job)
    session.commit()


def fail_job(session: Session, job: JobRow, error: str):
    """仕事を「失敗」にする"""
    job.status = FAILED
    job.error = error
    session.add(job)
    session.commit()


def requeue_running_jobs(session: Session) -> int:
    """「実行中」のまま残っている仕事を「待ち」に戻し、戻した件数を返す"""
    # ワーカーが処理の途中で止まると、その仕事は「実行中」のまま残ってしまう。
    # ワーカーを1つだけ動かす前提で、起動時にこれを呼んでやり直せるようにする
    result = session.exec(
        update(JobRow).where(col(JobRow.status) == RUNNING).values(status=PENDING)
    )
    session.commit()
    return result.rowcount
