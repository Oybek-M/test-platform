# test-platform — Implementation Plan

> **Ijrochi (Sonnet) uchun:** Bu plan Sonnet modelida bosqichma-bosqich bajariladi. Har task **Files → What → Key details → Verify** tuzilishida. Kod bloklari — faqat *tricky/qaror-kritik* joylarda (modellar, TOTP, baholash, import, xavfsizlik). Oddiy CRUD/UI kodini o'zing yoz, mavjud pattern va konventsiyalarga amal qil. Har task oxirida commit qil.

**Goal:** Kompyuter savodxonligi (va keyingi kurslar) uchun dinamik onlayn imtihon platformasi — admin savol/guruh/imtihon boshqaradi, o'quvchilar rotatsion parol bilan kirib test topshiradi, natija avtomatik baholanadi.

**Architecture:** FastAPI (Python) backend + PostgreSQL + Vue 3 SPA frontend, Docker Compose bilan `test.2007.uz`ga deploy. Backend biznes-mantiq (baholash, TOTP, import, imtihon oqimi) + JWT admin auth; o'quvchilar auth'siz, TOTP + vaqt oynasi bilan himoyalangan.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, pyotp, openpyxl, python-docx, passlib[bcrypt], python-jose · Vue 3, Vite, TypeScript, Pinia, Vue Router, axios · Docker, Nginx, certbot.

**Spec:** `docs/2026-07-23-test-platform-design.md` (bu planning manbasi — ziddiyat bo'lsa spec ustun).

---

## Umumiy tamoyillar (butun plan bo'yicha)

- **DRY, YAGNI, TDD (backend mantig'i uchun):** grading, TOTP verify, import parser, exam start/submit mantig'iga pytest testlari yoziladi. UI komponentlariga qat'iy TDD shart emas — qo'lda/integration checkpoint bilan tekshiriladi.
- **Xavfsizlik invariantlari (buzilmasin):**
  - O'quvchi API javoblarida `correct_index` **hech qachon** bo'lmaydi.
  - Baholash faqat serverda. Frontend ballni hisoblamaydi.
  - `totp_secret` faqat admin API'da; o'quvchiga chiqmaydi.
- **Soft-delete:** hamma asosiy jadval `is_deleted` bilan; querylarda `is_deleted == False` filtri.
- **Commit tez-tez:** har mantiqiy blok tugagach.
- **Migratsiya:** har model o'zgarishida `alembic revision --autogenerate` + `alembic upgrade head`.

---

# FAZA 1 — Yadro (MVP, ertagi imtihon uchun shart)

## Task 1.1: Loyiha skeleti va konfiguratsiya

**Files:**
- Create: `backend/requirements.txt`, `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`, `backend/app/database.py`
- Create: `backend/.env.example`, `.gitignore`, `README.md`

**What:** FastAPI ilovasi ishga tushadigan minimal skelet + Postgres ulanish + sozlamalar.

**Key details:**
- `config.py` — `pydantic-settings` bilan `.env` o'qiydi: `DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `CORS_ORIGINS`. **Admin parol `.env`da YO'Q** (Task 1.3 — CLI orqali o'rnatiladi, DB'da hash).
- `database.py` — SQLAlchemy 2.x `create_engine` + `SessionLocal` + `Base` (declarative) + `get_db()` dependency.
- `main.py` — `FastAPI(title="test-platform")`, CORS middleware, `/api/health` endpoint (`{"status":"ok"}`).
- `.env.example` da barcha kalitlar namuna qiymat bilan. `.gitignore` da `.env`, `__pycache__`, `node_modules`, `dist`, `*.db`.

**requirements.txt (aniq):**
```
fastapi
uvicorn[standard]
sqlalchemy>=2.0
alembic
psycopg2-binary
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
pyotp
openpyxl
python-docx
python-multipart
```

**Verify:**
- `pip install -r requirements.txt` xatosiz.
- `uvicorn app.main:app --reload` → `GET http://localhost:8000/api/health` → `{"status":"ok"}`.
- **Commit:** `chore: backend skeleton + config`

## Task 1.2: SQLAlchemy modellar

**Files:**
- Create: `backend/app/models/__init__.py`, `course.py`, `group.py`, `student.py`, `question.py`, `exam.py`, `attempt.py`, `admin.py`

**What:** Spec §3 dagi barcha jadvallar. Har fayl bitta model.

**Key details (ustunlar spec §3 bo'yicha, aniq):**
- Umumiy: `id` (PK, int autoincrement), `created_at` (server_default now), `is_deleted` (Boolean, default False) — Admin'dan tashqari.
- `Course`: `name` (String, not null), `description` (Text, nullable), `grading_scale` (JSON, default spec §3.1 dagi 5-darajali massiv).
- `Group`: `course_id` (FK→course), `name`.
- `Student`: `group_id` (FK→group), `full_name`.
- `Question`: `course_id` (FK), `text` (Text), `options` (JSON list[str]), `correct_index` (Integer), `topic` (String, nullable), `is_active` (Boolean default True).
- `Exam`: `course_id`, `group_id` (FK'lar), `title`, `starts_at` (DateTime), `duration_minutes` (Int), `question_count` (Int), `shuffle_questions` (Bool default True), `shuffle_options` (Bool default True), `allow_resume` (Bool default False), `show_result_to_student` (Bool default True), `totp_secret` (String), `totp_digits` (Int default 6), `totp_period` (Int default 30), `status` (String default "draft"), `access_code` (String, unique index).
- `Attempt`: `exam_id`, `student_id` (FK'lar), `started_at`, `submitted_at` (nullable), `question_ids` (JSON list[int]), `answers` (JSON dict), `score` (Int nullable), `total` (Int nullable), `percent` (Int nullable), `grade` (String nullable), `status` (String default "in_progress"). Unique constraint `(exam_id, student_id)`.
- `Admin`: `username` (unique), `password_hash`.

**Verify:**
- `python -c "from app.models import *"` importda xato yo'q.
- **Commit:** `feat: SQLAlchemy models`

## Task 1.3: Alembic sozlash + migratsiya + create_admin CLI

**Files:**
- Create: `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/` (autogenerate)
- Create: `backend/app/core/security.py` (parol hash/verify, JWT create/decode)
- Create: `backend/scripts/create_admin.py`

**What:** Migratsiya infratuzilmasi + adminni **CLI orqali** yaratish (parol `.env`da emas, DB'da faqat hash).

**Key details:**
- `alembic/env.py` — `target_metadata = Base.metadata`, `DATABASE_URL`ni config'dan oladi.
- `security.py`:
  ```python
  from passlib.context import CryptContext
  from jose import jwt
  from datetime import datetime, timedelta, timezone

  pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
  def hash_password(p): return pwd.hash(p)
  def verify_password(p, h): return pwd.verify(p, h)
  def create_token(sub, secret, minutes):
      exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
      return jwt.encode({"sub": sub, "exp": exp}, secret, algorithm="HS256")
  def decode_token(token, secret): return jwt.decode(token, secret, algorithms=["HS256"])
  ```
- `create_admin.py` — interaktiv `getpass` (yoki `--username --password` argument) bilan admin yaratadi/yangilaydi; DB'ga faqat `hash_password(...)` yoziladi, ochiq parol saqlanmaydi. `.env`dan parol o'qimaydi. Takror ishga tushsa mavjud adminni yangilaydi (upsert).

**Verify:**
- `alembic upgrade head` → jadvallar yaratildi (`\dt` da ko'rinadi).
- `python scripts/create_admin.py` (parol so'raydi) → DB'da admin qatori (faqat hash, ochiq parol yo'q).
- **Commit:** `feat: alembic migrations + create_admin CLI + security core`

## Task 1.4: Admin auth (login + JWT dependency)

**Files:**
- Create: `backend/app/schemas/auth.py`, `backend/app/api/admin/auth.py`, `backend/app/api/deps.py`
- Modify: `backend/app/main.py` (router include)

**What:** `POST /api/admin/auth/login` → JWT. `get_current_admin` dependency admin endpointlarni himoyalaydi. Admin o'z username+parolini o'zgartira oladi (`/me`).

**Key details:**
- Login: username+parol tekshiradi (`verify_password`) → `create_token`. Xato → 401.
- `deps.py`: `get_current_admin(Authorization: Bearer)` → tokenni decode qiladi, admin qaytaradi, aks holda 401.
- `GET /api/admin/auth/me` → joriy admin (`{id, username}`), token talab qiladi.
- `PUT /api/admin/auth/me` `{current_password, new_username?, new_password?}` — `verify_password(current_password)` **majburiy** (xato → 403); `new_password` berilsa `hash_password` bilan yangilanadi; `new_username` bo'sh bo'lmasin va unique (band bo'lsa → 409). Kamida bittasi (username yoki password) berilishi kerak.

**Verify (test):**
- `pytest` — to'g'ri parol → token; noto'g'ri → 401; himoyalangan endpoint token'siz → 401.
- Profil o'zgartirish: noto'g'ri `current_password` → 403; to'g'ri → username/parol yangilanadi; keyin **yangi parol bilan login 200**, eski parol bilan 401.
- **Commit:** `feat: admin auth (login + jwt + self profile change)`

## Task 1.5: Kurs CRUD + baholash shkalasi

**Files:**
- Create: `backend/app/schemas/course.py`, `backend/app/api/admin/courses.py`
- Modify: `main.py` (router)

**What:** Kurs yaratish/ro'yxat/tahrirlash/o'chirish (soft-delete) + `grading_scale` tahrirlash.

**Key details:**
- Pydantic: `CourseCreate{name, description?, grading_scale?}`, `CourseOut{...}`. `grading_scale` default spec §3.1.
- Validatsiya: `grading_scale` — kamida bitta element, har birida `grade` (str) va `min` (0–100 int).
- Barcha endpoint `Depends(get_current_admin)`.

**Verify:** CRUD qo'lda (curl yoki Swagger `/docs`) ishlaydi; soft-delete'dan keyin ro'yxatda ko'rinmaydi. **Commit:** `feat: course CRUD + grading scale`

## Task 1.6: Baholash servisi (TDD)

**Files:**
- Create: `backend/app/services/grading.py`, `backend/tests/test_grading.py`

**What:** Foiz va harf bahoni hisoblovchi sof funksiyalar.

**Key details:**
```python
def calc_percent(score: int, total: int) -> int:
    return 0 if total == 0 else round(score / total * 100)

def calc_grade(percent: int, scale: list[dict]) -> str:
    # scale: [{"grade":"A","min":90}, ...]. min bo'yicha kamayuvchi tartibda,
    # percent >= min bo'lgan birinchi grade. Hech biriga tushmasa oxirgisi.
    for item in sorted(scale, key=lambda x: x["min"], reverse=True):
        if percent >= item["min"]:
            return item["grade"]
    return scale[-1]["grade"] if scale else "F"
```

**Verify (test — avval yoz, fail bo'lsin, keyin implement):**
- 9/10 → 90% → "A"; 7/10 → 70% → "C"; 5/10 → 50% → "F"; 0/0 → 0% → "F".
- Maxsus shkala bilan ham to'g'ri.
- `pytest tests/test_grading.py -v` → PASS. **Commit:** `feat: grading service (percent + letter grade)`

## Task 1.7: TOTP servisi (TDD)

**Files:**
- Create: `backend/app/services/totp.py`, `backend/tests/test_totp.py`

**What:** Imtihon uchun rotatsion kod generatsiya/tekshirish (4/6 xona, 30/60s).

**Key details:**
```python
import pyotp, time

def new_secret() -> str:
    return pyotp.random_base32()

def _totp(secret, digits, period):
    return pyotp.TOTP(secret, digits=digits, interval=period)

def current_code(secret, digits=6, period=30) -> tuple[str, int]:
    t = _totp(secret, digits, period)
    code = t.now()
    seconds_left = period - (int(time.time()) % period)
    return code, seconds_left

def verify_code(secret, code, digits=6, period=30) -> bool:
    return _totp(secret, digits, period).verify(code, valid_window=1)
```

**Verify (test):**
- `current_code` bilan olingan kod darhol `verify_code`'da True.
- `digits=4` → 4 xonali kod. `period=60` → `seconds_left <= 60`.
- Noto'g'ri kod → False.
- **Commit:** `feat: totp service (rotating exam code)`

## Task 1.8: xlsx import — savollar (TDD)

**Files:**
- Create: `backend/app/services/imports.py`, `backend/tests/test_import_questions.py`, `backend/tests/fixtures/questions_sample.xlsx`
- Create: `backend/app/templates/samples/questions_template.xlsx` (namuna, generatsiya skripti yoki qo'lda)

**What:** xlsx → parsed savollar ro'yxati + validatsiya + preview.

**Key details:**
- Kontrakt: `parse_questions_xlsx(file_bytes) -> {"questions": [...], "errors": [...]}`.
- Har savol: `{"text", "options": [...], "correct_index", "topic"}`.
- Ustunlar (spec §7.1): `savol, variant_A..variant_D, togri_javob, mavzu`. Bo'sh variant ustunlari tashlanadi. `togri_javob` A/B/C/D yoki 1–4 → 0-based index.
- Xato holatlar: savol matni bo'sh, <2 variant, `togri_javob` noto'g'ri → `errors`ga qator raqami bilan.

**Verify (test):**
- Namunaviy 3-qatorli xlsx → 3 savol, `correct_index` to'g'ri.
- Buzuq qator → `errors`da.
- **Commit:** `feat: xlsx question import parser + sample template`

## Task 1.9: Savol boshqaruvi API (qo'lda + import)

**Files:**
- Create: `backend/app/schemas/question.py`, `backend/app/api/admin/questions.py`
- Modify: `main.py`

**What:** Kurs savollari CRUD + `POST .../import` (preview→confirm) + namuna yuklab olish.

**Key details:**
- `GET /api/admin/courses/{cid}/questions` (filtr: `topic`, `is_active`).
- `POST` (qo'lda bitta), `PUT/{qid}`, `DELETE/{qid}` (soft-delete).
- `POST /api/admin/courses/{cid}/questions/import` — `multipart` xlsx → `imports.parse_questions_xlsx` → agar `errors` bo'lsa 422 + preview; `confirm=true` bo'lsa bazaga yozadi.
- `GET /api/admin/samples/questions.xlsx` → namuna fayl (FileResponse).

**Verify:** Swagger orqali import → savollar bazada. **Commit:** `feat: question management API + import + sample`

## Task 1.10: Guruh + o'quvchi API (text + xlsx)

**Files:**
- Create: `backend/app/schemas/group.py`, `backend/app/schemas/student.py`, `backend/app/api/admin/groups.py`
- Modify: `imports.py` (`parse_students_xlsx`), `main.py`
- Create: `backend/tests/test_import_students.py`, `backend/app/templates/samples/students_template.xlsx`

**What:** Guruh CRUD + o'quvchilarni text (har qator bitta F.I.Sh) yoki xlsx (bitta ustun) bilan qo'shish.

**Key details:**
- `POST /api/admin/groups/{gid}/students` — body `{"text": "..."}` yoki `multipart` xlsx. Har ikkisi ham F.I.Sh ro'yxatiga aylanadi, bo'sh qatorlar tashlanadi, takrorlar ogohlantiriladi.
- `parse_students_xlsx(bytes) -> list[str]`.
- Namuna: `GET /api/admin/samples/students.xlsx`.

**Verify (test):** text 3 qator → 3 student; xlsx 3 qator → 3 student. **Commit:** `feat: group + student management (text/xlsx import)`

## Task 1.11: Imtihon yaratish/boshqarish API

**Files:**
- Create: `backend/app/schemas/exam.py`, `backend/app/api/admin/exams.py`, `backend/app/services/access_code.py`
- Modify: `main.py`

**What:** Imtihon CRUD + holat boshqaruvi + jonli TOTP kod endpoint.

**Key details:**
- Yaratishda: `totp_secret = totp.new_secret()`, `access_code = access_code.generate()` (6–8 belgi, unique tekshiruv).
- Body: `course_id, group_id, title, starts_at, duration_minutes, question_count, shuffle_questions, shuffle_options, allow_resume, show_result_to_student, totp_digits(4|6), totp_period(30|60)`. Validatsiya: `totp_digits in {4,6}`, `totp_period in {30,60}`, `question_count <= faol savollar soni`.
- `POST /api/admin/exams/{id}/status` — `{status}` (draft|scheduled|open|closed).
- `GET /api/admin/exams/{id}/totp` → `{"code": ..., "seconds_left": ...}` (`totp.current_code`).
- **`totp_secret` javoblarda chiqmasin** (Pydantic `ExamOut`da yo'q).

**Verify:** imtihon yaratiladi, `/totp` jonli kod qaytaradi, status o'zgaradi. **Commit:** `feat: exam management API + live totp code`

## Task 1.12: O'quvchi imtihon oqimi API (public) — eng muhim

**Files:**
- Create: `backend/app/schemas/exam_public.py`, `backend/app/api/exam/flow.py`, `backend/app/services/exam_engine.py`
- Create: `backend/tests/test_exam_engine.py`
- Modify: `main.py`

**What:** Spec §5 oqimi. Auth'siz, lekin TOTP + vaqt oynasi + Attempt cheklovlari bilan.

**Key details / kontraktlar:**
- `GET /api/exam/{access_code}` → `{title, group_name, status, starts_at, duration_minutes, is_open_now}`. **Savollar yo'q, secret yo'q.**
- `is_open_now` = `status=="open"` AND `starts_at <= now <= starts_at + duration`.
- `POST /api/exam/{access_code}/verify-code` `{code}` → `totp.verify_code(...)`; noto'g'ri → 403. To'g'ri → qisqa muddatli "gate token" yoki oddiy `{"ok":true}` (MVP: keyingi qadamlar ham `code`ni qayta yuboradi — soddaroq: `code`ni har so'rovda qayta tekshirish o'rniga, MVP'da `verify-code` muvaffaqiyatli bo'lsa frontend ism tanlashga o'tadi; `start` da yana bir marta tekshiriladi).
- `GET /api/exam/{access_code}/students?code=...` → band bo'lmagan o'quvchilar (`[{id, full_name}]`). Band = shu exam uchun Attempt bor va (`submitted`/`expired` va `allow_resume=false`).
- `POST /api/exam/{access_code}/start` `{student_id, code}` → serverda:
  - `is_open_now` va `verify_code` tekshiriladi (aks holda 403).
  - Mavjud Attempt: agar `in_progress` va `allow_resume` → o'shani qaytaradi; agar tugagan va `allow_resume=false` → 409.
  - Yangi Attempt: `exam_engine.pick_questions(exam)` — faol savollardan `question_count` ta tasodifiy, `shuffle_questions`/`shuffle_options` bo'yicha aralashtirilgan. `question_ids` saqlanadi.
  - Qaytaradi: `{attempt_id, ends_at, questions: [{id, text, options}]}` — **`correct_index` YO'Q.**
- `POST /api/exam/{access_code}/submit` `{attempt_id, answers}` → serverda baholaydi:
  - Vaqt tekshiruvi: `now > started_at + duration` bo'lsa `status=expired`, lekin baribir kelgan javoblarni baholaydi.
  - Har savol uchun `answers[qid] == question.correct_index` → to'g'ri. `score/total` → `grading.calc_percent/calc_grade` (kurs `grading_scale`).
  - Attempt yangilanadi (`answers, score, total, percent, grade, submitted_at, status=submitted`).
  - Qaytaradi: `show_result_to_student` true bo'lsa `{score, total, percent, grade}`, aks holda `{"submitted": true}`.

**exam_engine.py sof funksiyalar (TDD):**
```python
def pick_questions(active_questions, count, shuffle_q, shuffle_o):
    # random.sample count ta; shuffle_o bo'lsa options aralashadi va correct_index moslashtiriladi
    ...
def grade_attempt(question_map, question_ids, answers):
    # returns (score, total)
    ...
```

**Verify (test — asosiy):**
- `pick_questions`: count ta savol; options aralashsa `correct_index` to'g'ri qoladi (aralashgan variantdagi to'g'ri javob indeksi mos).
- `grade_attempt`: to'g'ri/noto'g'ri sanash.
- Integration: to'liq oqim (verify→start→submit) 200; `correct_index` hech qayerda chiqmaydi (javob JSON tekshiriladi).
- **Commit:** `feat: student exam flow API + engine (verify/start/submit)`

## Task 1.13: Frontend skelet + admin auth + layout

**Files:**
- Create: `frontend/` (Vite scaffold: `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.ts`, `src/App.vue`)
- Create: `src/api/client.ts` (axios + JWT interceptor), `src/stores/auth.ts` (Pinia), `src/router/index.ts`
- Create: `src/views/admin/LoginView.vue`, `src/views/admin/ProfileView.vue`, `src/components/AdminLayout.vue`

**What:** Vue skelet, admin login, token saqlash, himoyalangan route guard, admin layout (sidebar: Kurslar/Savollar/Guruhlar/Imtihonlar/Natijalar/Profil). **Profil sahifasi:** `GET/PUT /api/admin/auth/me` bilan username+parol o'zgartirish (joriy parolni tasdiqlab).

**Key details:**
- axios `baseURL: /api`; request interceptor Bearer token qo'shadi; 401 → login'ga.
- Router guard: admin route'lar token talab qiladi.
- `vite.config.ts` dev proxy: `/api` → `http://localhost:8000`.

**Verify:** `npm run dev` → login ishlaydi, token bilan admin layout ochiladi; Profil sahifasida username/parol o'zgartirib, **yangi parol bilan qayta login** ishlaydi. **Commit:** `feat: frontend skeleton + admin auth + layout + profile`

## Task 1.14: Admin UI — Kurslar + Savollar

**Files:**
- Create: `src/views/admin/CoursesView.vue`, `src/views/admin/QuestionsView.vue`
- Create: `src/components/QuestionForm.vue`, `src/components/ImportDialog.vue`

**What:** Kurs ro'yxati/yaratish/tahrirlash + baholash shkalasi tahriri; kurs ichida savollar ro'yxati, qo'lda qo'shish, xlsx import (preview→confirm), namuna yuklab olish.

**Verify (qo'lda):** kurs yaratish → savol qo'lda + import → ro'yxatda ko'rinadi. **Commit:** `feat: admin UI — courses + questions`

## Task 1.15: Admin UI — Guruhlar + O'quvchilar + Imtihonlar

**Files:**
- Create: `src/views/admin/GroupsView.vue`, `src/views/admin/ExamsView.vue`, `src/views/admin/ExamFormView.vue`, `src/components/StudentImport.vue`

**What:** Guruh CRUD + o'quvchi (text/xlsx) qo'shish; imtihon yaratish formasi (barcha sozlamalar: sana/vaqt picker, davomiylik, savol soni, aralashtirish, qayta-kirish, natija-ko'rsatish, TOTP 4/6 · 30/60 tanlash); imtihon ro'yxati + status boshqaruvi + havola nusxalash.

**Verify (qo'lda):** to'liq imtihon yaratish mumkin. **Commit:** `feat: admin UI — groups + students + exams`

## Task 1.16: Admin UI — Jonli TOTP kod ekrani

**Files:**
- Create: `src/views/admin/LiveCodeView.vue`

**What:** Imtihon uchun katta shriftda joriy kod + qolgan soniya progress bar. Har soniya `GET .../totp` yoki `seconds_left` bo'yicha yangilanadi (2–3 soniyada bir poll).

**Verify (qo'lda):** kod har 30/60s da yangilanadi. **Commit:** `feat: admin live totp code screen`

## Task 1.17: O'quvchi UI — to'liq oqim

**Files:**
- Create: `src/views/exam/ExamEntryView.vue` (holat), `PasswordView.vue` (kod), `PickNameView.vue` (ism), `ExamView.vue` (test+taymer), `ResultView.vue`
- Create: `src/stores/exam.ts`

**What:** Spec §5 oqimi. Route `/e/:accessCode`. Kod → ism → savollar (bittalab yoki bitta sahifada) + taymer (`ends_at`gacha) → topshirish → natija. Taymer 0 bo'lsa avtomatik submit.

**Key details:** Savollar API'dan kelganidek ko'rsatiladi (`correct_index` yo'q). Javoblar `{question_id: index}` yig'iladi. Sahifa refresh'da `allow_resume` bo'lsa davom (localStorage'da `attempt_id`).

**Verify (qo'lda, uchma-uch):** admin imtihon `open` qiladi → o'quvchi `/e/<code>` → kod → ism → test → topshirish → natija/baho ko'rinadi; qayta kirmoqchi bo'lsa bloklanadi. **Commit:** `feat: student exam UI (full flow)`

## Task 1.18: Natijalar UI + Faza 1 uchma-uch sinov

**Files:**
- Create: `src/views/admin/ResultsView.vue`

**What:** Imtihon bo'yicha natijalar jadvali (F.I.Sh, ball, foiz, baho, vaqt, holat).

**Faza 1 acceptance (qo'lda to'liq ssenariy):**
1. Admin login. 2. Kurs "Kompyuter savodxonligi" + 10+ savol (qo'lda + xlsx). 3. Guruh + 3 test-o'quvchi. 4. Imtihon (5 savol, 10 daqiqa, TOTP 6/30, resume off) yaratish → `open`. 5. Jonli kod ekranini ochish. 6. Boshqa brauzer/inkognitoda `/e/<code>` → kod → ism → test → topshirish → baho. 7. Qayta kirish bloklanadi. 8. Admin natijalarda ko'radi.

**Verify:** Yuqoridagi 8 qadam ishlaydi. **Commit:** `feat: results UI + phase-1 e2e verified`

---

# FAZA 2 — To'liqlik va Deploy

## Task 2.1: docx import — savollar (TDD)

**Files:** Modify `imports.py` (`parse_questions_docx`); Create `tests/test_import_questions_docx.py`, `app/templates/samples/questions_template.docx`; Modify `questions.py` API (docx qabul qilsin), `ImportDialog.vue` (docx tanlov).

**What:** Spec §7.2 formati. `python-docx` bilan paragraflarni o'qib savol/variant/to'g'ri javob (`*`/`[x]`) ajratadi.

**Verify (test):** namunaviy docx → to'g'ri savollar. **Commit:** `feat: docx question import`

## Task 2.2: Natijalar xlsx eksport

**Files:** Modify `exams.py` (`GET /api/admin/exams/{id}/results/export`), `ResultsView.vue` (Eksport tugmasi). Create `app/services/exports.py`.

**What:** `openpyxl` bilan natijalarni xlsx qilib beradi (FileResponse).

**Verify (qo'lda):** eksport fayli to'g'ri ochiladi. **Commit:** `feat: results xlsx export`

## Task 2.3: Sozlamalar/tahrirlash UI to'ldirish + jonli kod polish

**Files:** Modify tegishli admin view'lar.

**What:** Imtihon/savol/guruh tahrirlash oqimlarini to'liqlash; jonli kod ekranini "to'liq ekran" (fullscreen) rejimi bilan sayqallash.

**Verify (qo'lda):** tahrirlash va fullscreen ishlaydi. **Commit:** `feat: settings/edit UI polish + fullscreen live code`

## Task 2.4: Dockerizatsiya (lokal)

**Files:** Create `backend/Dockerfile`, `frontend/Dockerfile`, `nginx/default.conf`, `docker-compose.yml`, `docker-compose.override.yml.example`, `.env.example` (deploy kalitlari).

**What:**
- `backend/Dockerfile` — python, uvicorn.
- `frontend/Dockerfile` — multi-stage: `npm run build` → statik `dist` → nginx bilan beriladi (yoki alohida nginx service `dist`ni mount qiladi).
- `nginx/default.conf` — `/api` → backend:8000, qolgani → frontend statik; gzip.
- `docker-compose.yml` — `postgres`, `backend` (entrypoint: `alembic upgrade head && uvicorn`), `nginx`. Admin **bir martalik** yaratiladi: `docker compose exec backend python scripts/create_admin.py` (parol `.env`da emas, interaktiv kiritiladi).

**Verify:** `docker compose up --build` → `http://localhost` da to'liq ishlaydi (admin + o'quvchi oqimi). **Commit:** `feat: docker compose (backend + postgres + nginx)`

## Task 2.5: VPS diagnostikasi

**Files:** Create `docs/vps-diagnostics.md` (natijalar yoziladi).

**What (spec §14 — SSH orqali Contabo VPS):**
```bash
docker --version && docker compose version   # Docker bormi
df -h                                         # disk
free -m                                       # xotira
docker ps                                     # ishlab turgan konteynerlar
ss -tlnp | grep -E ':80|:443'                 # portlar bandmi (nginx bormi)
```
- DNS: `test.2007.uz` A-record VPS IP'ga qo'yilgani (registrar panelida). `dig +short test.2007.uz`.
- Natijaga qarab qaror: mavjud host-Nginx'ga reverse-proxy `server` bloki qo'shamiz **yoki** compose'dagi Nginx'ni 80/443'ga chiqaramiz (agar bo'sh bo'lsa).

**Verify:** diagnostika natijasi `docs/vps-diagnostics.md`da; deploy usuli tanlandi. **Commit:** `docs: vps diagnostics + deploy decision`

## Task 2.6: Deploy — test.2007.uz + TLS

**Files:** Modify deploy config (host nginx server block yoki compose nginx), Create `docs/deploy.md`.

**What:**
- Kodni VPS'ga (git clone/pull yoki rsync), `.env` production qiymatlar (kuchli `JWT_SECRET`, admin parol).
- `docker compose -f docker-compose.yml up -d --build`.
- Nginx `test.2007.uz` server bloki → platformaga proxy.
- `certbot --nginx -d test.2007.uz` → TLS.
- Smoke test: `https://test.2007.uz` admin login + o'quvchi oqimi.

**Verify:** `https://test.2007.uz` da to'liq ishlaydi (uchma-uch). **Commit:** `chore: production deploy (test.2007.uz + tls)`

---

# FAZA 3 — Sayqal

## Task 3.1: Natijalar analitikasi

**Files:** Modify `exams.py` (`GET .../results/stats`), Create `src/views/admin/AnalyticsView.vue`.

**What:** Imtihon bo'yicha: o'rtacha foiz, baho taqsimoti (A/B/C/D/F soni), eng qiyin savollar (eng ko'p xato). Oddiy jadval/bar.

**Verify (qo'lda):** statistika to'g'ri hisoblanadi. **Commit:** `feat: results analytics`

## Task 3.2: Savol mavzular bo'yicha statistika

**Files:** Modify analytics endpoint/view.

**What:** Mavzu (`topic`) kesimida to'g'ri/noto'g'ri foiz — qaysi mavzu qiyin bo'lganini ko'rsatadi.

**Verify (qo'lda):** mavzu statistikasi ko'rinadi. **Commit:** `feat: topic-level statistics`

## Task 3.3: Test generatsiya oqimini tayyorlash

**Files:** Create `docs/test-generation-workflow.md`.

**What:** Kelajakda Oybek chatga qaytib "falon kurs uchun test generatsiya qil" deganda, savollar to'g'ridan-to'g'ri qo'shilishi uchun: standart xlsx/JSON kontrakt hujjatlashtiriladi + (ixtiyoriy) `POST /api/admin/courses/{cid}/questions/bulk` JSON endpoint qo'shiladi.

**Verify:** hujjat + (agar qo'shilsa) bulk endpoint test bilan. **Commit:** `feat: bulk question import endpoint + generation workflow doc`

---

## Self-review qaydi (plan → spec qamrovi)

- Admin auth + profil o'zgartirish (username/parol UI) ✓(1.4,1.13) · Kurs+shkala ✓(1.5) · Savol qo'lda/xlsx/docx ✓(1.8,1.9,2.1) · Namuna fayllar ✓(1.8,1.10,2.1) · Guruh+o'quvchi text/xlsx ✓(1.10) · Imtihon+TOTP 4-6/30-60 ✓(1.11,1.15) · Jonli kod ✓(1.16) · O'quvchi oqimi+resume+natija ✓(1.12,1.17) · Baholash sozlanadigan ✓(1.5,1.6) · Natijalar+eksport ✓(1.18,2.2) · Xavfsizlik (correct_index leak yo'q) ✓(1.12) · Docker+deploy+TLS ✓(2.4,2.6) · VPS diagnostika ✓(2.5) · Analitika/generatsiya ✓(3.x).
- Type konsistensiya: `pick_questions`, `grade_attempt`, `current_code`, `verify_code`, `calc_percent`, `calc_grade` nomlar plan bo'ylab bir xil.
- Placeholder yo'q.
