# CSV 書き出しの API（/api/exports/...）をまとめたファイル（第13章で追加）
# Web アプリは「仕事を登録する」「状態を答える」「できたファイルを渡す」だけで、
# 時間のかかる処理そのものはワーカー（worker.py）が行う

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import database
import tasks
from dependencies import SessionDep
from schemas import Job

router = APIRouter(prefix="/api/exports", tags=["CSV 書き出し API"])


def get_job_or_404(session: SessionDep, job_id: int) -> database.JobRow:
    job = database.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="指定された仕事が見つかりません")
    return job


# 仕事の登録  POST /api/exports
# 202 は「受け付けた（処理はまだ終わっていない）」という意味のステータスコード
@router.post("", response_model=Job, status_code=202)
def create_export(session: SessionDep):
    return database.add_job(session)


# 状態の確認  GET /api/exports/1
@router.get("/{job_id}", response_model=Job)
def read_export(job_id: int, session: SessionDep):
    return get_job_or_404(session, job_id)


# できたファイルのダウンロード  GET /api/exports/1/download
@router.get("/{job_id}/download")
def download_export(job_id: int, session: SessionDep):
    job = get_job_or_404(session, job_id)
    if job.status != database.DONE or job.result_file is None:
        raise HTTPException(status_code=409, detail="まだファイルができていません")

    path = Path(tasks.EXPORT_DIR) / job.result_file
    # FileResponse: ファイルをそのまま返す。filename を付けるとダウンロードとして扱われる
    return FileResponse(path, filename=job.result_file, media_type="text/csv")
