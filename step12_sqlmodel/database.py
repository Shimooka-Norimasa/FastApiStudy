# データベース操作をまとめたファイル（SQLModel 版）
# 第11章との違い: SQL を自分で書かず、Python のクラスとメソッドでデータベースを操作する

from sqlmodel import Field, Session, SQLModel, col, create_engine, select

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
