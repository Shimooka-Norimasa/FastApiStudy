# Pydantic モデル: API でやり取りする JSON の「形」を定義するファイル

from pydantic import BaseModel, ConfigDict, Field

MAX_TITLE_LENGTH = 100


# 追加するときに受け取る JSON の形  例) {"title": "牛乳を買う"}
class TodoCreate(BaseModel):
    # 文字列の前後の空白を自動で取り除く設定
    model_config = ConfigDict(str_strip_whitespace=True)

    # Field で「1文字以上、100文字以下」というルールを付ける
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)


# 更新するときに受け取る JSON の形
# どちらも省略可能（None）にして、送られてきた項目だけを更新する
# 例) {"done": true}  /  {"title": "牛乳を2本買う"}
class TodoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=MAX_TITLE_LENGTH)
    done: bool | None = None


# 返すときの JSON の形  例) {"id": 1, "title": "牛乳を買う", "done": false}
class Todo(BaseModel):
    id: int
    title: str
    done: bool


# 第13章で追加: 仕事（CSV 書き出し）の状態を返すときの JSON の形
# 例) {"id": 1, "status": "pending", "error": null}
class Job(BaseModel):
    id: int
    status: str            # "pending" / "running" / "done" / "failed"
    error: str | None
