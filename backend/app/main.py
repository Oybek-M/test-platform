from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin.auth import router as admin_auth_router
from app.api.admin.courses import router as admin_courses_router
from app.api.admin.exams import router as admin_exams_router
from app.api.admin.groups import router as admin_groups_router
from app.api.admin.questions import router as admin_questions_router
from app.api.admin.samples import router as admin_samples_router
from app.api.exam.flow import router as exam_flow_router
from app.config import settings

app = FastAPI(title="test-platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_auth_router)
app.include_router(admin_courses_router)
app.include_router(admin_questions_router)
app.include_router(admin_groups_router)
app.include_router(admin_exams_router)
app.include_router(admin_samples_router)
app.include_router(exam_flow_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
