from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/admin/samples", tags=["admin-samples"])

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "samples"

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/students.xlsx")
def download_students_sample():
    return FileResponse(
        path=SAMPLES_DIR / "students_template.xlsx",
        filename="students_template.xlsx",
        media_type=XLSX_MEDIA_TYPE,
    )


@router.get("/questions.xlsx")
def download_questions_sample():
    return FileResponse(
        path=SAMPLES_DIR / "questions_template.xlsx",
        filename="questions_template.xlsx",
        media_type=XLSX_MEDIA_TYPE,
    )
