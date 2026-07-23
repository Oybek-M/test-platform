# test-platform — Imtihon/Test platformasi (Dizayn spec)

- **Sana:** 2026-07-23
- **Muallif:** Oybek + Claude (brainstorming)
- **Holat:** Tasdiqlangan dizayn → implementation plan yoziladi
- **Loyiha papkasi:** `C:\Users\Oybek\Documents\Projects programming\DC\test-platform`
- **Domain (vaqtincha):** `test.2007.uz` subdomain (Contabo VPS)
- **Muhim:** Bu loyiha iBOS/UFL startaplariga aloqasi yo'q. Mustaqil, shaxsiy foydalanish uchun.

---

## 1. Maqsad va konteks

Kompyuter savodxonligi kursini yakunlagan guruhlardan **onlayn imtihon** olish uchun universal, dinamik platforma. Bitta guruh **ertaga** imtihon topshiradi; keyingi guruhlar (va boshqa yo'nalishlar — frontend, backend va h.k.) ham xuddi shu platformadan foydalanadi.

**Asosiy tamoyillar:**
- Deyarli hamma narsa dinamik: kurs, guruh, o'quvchilar ro'yxati, savollar, imtihon vaqti/davomiyligi — admin paneldan boshqariladi.
- O'quvchilar uchun to'liq auth/authorization **yo'q**; buning o'rniga rotatsion (har 30/60s almashuvchi) parol himoyasi.
- Savol bazasi yo'nalish (kurs) bo'yicha saqlanadi va qayta ishlatiladi.

## 2. Foydalanuvchi rollari

| Rol | Kim | Kirish usuli |
|---|---|---|
| **Admin** | Oybek (yagona) | Login + parol (JWT sessiya) |
| **O'quvchi** | Imtihon topshiruvchi | Auth yo'q → rotatsion parol + ro'yxatdan ism tanlash |

## 3. Ma'lumot modeli

Ierarxiya: **Course → Group → Student**, savollar **Course** bazasida, **Exam** bitta Group'ni nishonga oladi.

### 3.1. Course (Kurs / Yo'nalish)
Savol bazasi va baholash sozlamalari shu yerda.
- `id`, `name` (mas. "Kompyuter savodxonligi")
- `description` (ixtiyoriy)
- `grading_scale` (JSON) — sozlanadigan chegaralar, default:
  ```json
  [
    {"grade": "A", "min": 90},
    {"grade": "B", "min": 80},
    {"grade": "C", "min": 70},
    {"grade": "D", "min": 60},
    {"grade": "F", "min": 0}
  ]
  ```
- `created_at`, `is_deleted` (soft-delete)

### 3.2. Group (Guruh)
- `id`, `course_id` (FK), `name` (mas. "KS-2026-Aprel")
- `created_at`, `is_deleted`

### 3.3. Student (O'quvchi)
- `id`, `group_id` (FK), `full_name` (F.I.Sh)
- `created_at`, `is_deleted`
- Ism-familiya matn maydoniga (har qatorga bitta) yoki xlsx'dan import qilinadi.

### 3.4. Question (Savol)
- `id`, `course_id` (FK)
- `text` (savol matni)
- `options` (JSON massiv, mas. `["A varianti", "B varianti", "C", "D"]`) — 2–6 ta variant
- `correct_index` (0-dan boshlab, to'g'ri variant indeksi)
- `topic` (mavzu, ixtiyoriy — filtr va statistika uchun)
- `is_active` (bazadan tortishga kiritilsinmi)
- `created_at`, `is_deleted`

### 3.5. Exam (Imtihon)
- `id`, `course_id` (FK), `group_id` (FK), `title`
- `starts_at` (boshlanish sana+vaqt), `duration_minutes` (davomiylik)
- `question_count` (bazadan nechta tasodifiy savol tortiladi)
- `shuffle_questions` (bool), `shuffle_options` (bool)
- `allow_resume` (bool) — uzilganda qayta kirish; false bo'lsa topshirgach/chiqib ketgach bloklanadi
- `show_result_to_student` (bool, default true) — o'quvchi ballini ko'rsinmi
- **TOTP sozlamalari:** `totp_secret` (server yaratadi), `totp_digits` (4 yoki 6), `totp_period` (30 yoki 60 soniya)
- `status` — `draft` | `scheduled` | `open` | `closed`
- `access_code` (havola uchun qisqa noyob kod, mas. `/e/abc123`)
- `created_at`, `is_deleted`

**Holat mantiqi:** `open` va `starts_at`..(+duration) oynasi ichida bo'lsagina o'quvchi kira oladi. Admin qo'lda `open`/`closed` qila oladi.

### 3.6. Attempt (Urinish / Natija)
- `id`, `exam_id` (FK), `student_id` (FK)
- `started_at`, `submitted_at`
- `question_ids` (JSON — shu o'quvchiga tortilgan savollar tartibi, aralashtirilgan)
- `answers` (JSON — `{question_id: selected_index}`)
- `score` (to'g'ri javoblar soni), `total` (jami savol), `percent`, `grade`
- `status` — `in_progress` | `submitted` | `expired`
- **Cheklov:** har (exam_id, student_id) juftligi uchun bitta Attempt. `allow_resume=false` bo'lsa `submitted` yoki `expired` bo'lgach qayta boshlab bo'lmaydi.

### 3.7. Admin
- `id`, `username`, `password_hash` (bcrypt), `updated_at`
- Bitta admin **CLI buyruq** orqali yaratiladi (`scripts/create_admin.py`) — parol interaktiv kiritiladi, DB'ga faqat **bcrypt-hash** yoziladi. `.env`da admin parol **saqlanmaydi** (repo public bo'lishini hisobga olib).
- Admin keyinchalik **UI orqali o'z `username` va parolini o'zgartira oladi** (joriy parolni tasdiqlagan holda). Ya'ni haqiqiy saqlash joyi — DB, `.env` emas.

## 4. Admin panel (funksional talablar)

### 4.1. Kirish
- Login sahifasi → JWT token (localStorage). Barcha admin API'lari Bearer token talab qiladi.

### 4.2. Kurslar
- CRUD: yaratish, tahrirlash, o'chirish (soft-delete)
- Baholash shkalasini sozlash (chegaralarni qo'shish/o'chirish/o'zgartirish)

### 4.3. Savol bazasi (kurs ichida)
- Ro'yxat: mavzu bo'yicha filtr, qidiruv, faol/nofaol
- **Qo'lda kiritish:** matn + variantlar + to'g'ri javob + mavzu
- **xlsx import:** ustunlar `savol | variant_A | variant_B | variant_C | variant_D | togri_javob | mavzu`
  - `togri_javob` = `A`/`B`/`C`/`D` (yoki 1/2/3/4)
  - Bo'sh variant ustunlari e'tiborsiz (2–6 variant qo'llab-quvvatlanadi)
- **docx import (Faza 2):** raqamlangan savollar, `a) b) c) d)` variantlar, to'g'ri javob `*` yoki `[to'g'ri]` belgisi bilan
- **Namunaviy shablon fayllar:** admin panelda "Namuna yuklab olish" tugmasi (xlsx va docx) — to'g'ri format bilan
- Import oldidan **preview** (nechta savol topildi, xatolar) → tasdiqlash

### 4.4. Guruhlar va o'quvchilar
- Guruh CRUD (kursga bog'liq)
- O'quvchilar: (a) text maydon — har qatorga bitta F.I.Sh, (b) xlsx import (bitta ustun F.I.Sh)
- Namunaviy o'quvchilar xlsx shabloni

### 4.5. Imtihonlar
- Yaratish: kurs + guruh + title + sana/vaqt + davomiylik + savol soni + aralashtirish + qayta-kirish + natija-ko'rsatish + TOTP (4/6 xona, 30/60s)
- Holatni boshqarish: draft → scheduled → open → closed
- **Jonli parol ekrani:** imtihon uchun katta shriftda joriy rotatsion kod + qolgan soniya progress. Admin buni proyektorda ko'rsatadi yoki aytadi
- Imtihon havolasini nusxalash (`test.2007.uz/e/<access_code>`)

### 4.6. Natijalar
- Har imtihon bo'yicha jadval: F.I.Sh, ball, jami, foiz, baho, boshlagan/topshirgan vaqt, holat
- **xlsx eksport (Faza 2)**

### 4.7. Profil / Sozlamalar
- Admin o'z **username va parolini o'zgartiradi** (`GET/PUT /api/admin/auth/me`).
- Parol o'zgartirishda **joriy parol** tasdiqlanadi; yangi parol bcrypt-hash bo'lib DB'da yangilanadi.
- Boshlang'ich admin `scripts/create_admin.py` CLI orqali yaratiladi — `.env`da parol turmaydi.

## 5. O'quvchi imtihon oqimi

1. `test.2007.uz/e/<access_code>` ochadi → imtihon nomi, guruh, holat ko'rinadi
2. Imtihon `open` va vaqt oynasida bo'lmasa — "hali boshlanmagan / yopilgan" xabari
3. **Rotatsion parolni** kiritadi (server TOTP ±1 oyna toleransi bilan tekshiradi)
4. Guruh ro'yxatidan **o'z F.I.Sh'ini tanlaydi** — band (allaqachon topshirgan/boshlagan, resume yo'q) ismlar bloklangan
5. "Boshlash" → server Attempt yaratadi, savollarni tortadi (tasodifiy N ta, aralashtirilgan), `started_at` yoziladi
6. Savollarga javob beradi; yuqorida **taymer** (starts_at+duration yoki started_at+duration — pastini oling). Vaqt tugasa avtomatik topshiriladi
7. "Topshirish" → server baholaydi, natijani saqlaydi
8. `show_result_to_student=true` bo'lsa: ball, foiz, baho ko'rsatiladi (to'g'ri/noto'g'ri tafsilot ko'rsatilmaydi)
9. **Qayta kirish:** `allow_resume=false` bo'lsa — topshirgach yoki chiqib ketgach qayta kira olmaydi; imtihon `closed` bo'lsa hech kim kira olmaydi

**Taymer ishonchliligi:** server `started_at` va `duration`ni saqlaydi; frontend taymer faqat ko'rsatish uchun. Topshirishda server vaqtni qayta tekshiradi (muddat o'tgan bo'lsa `expired`).

## 6. Rotatsion parol (TOTP) — himoya mexanizmi

- Har imtihon `pyotp` bilan `totp_secret` oladi. Kod har `totp_period` (30/60s) da yangilanadi, `totp_digits` (4/6) xonali.
- **Admin tomoni:** `GET /api/admin/exams/{id}/totp` joriy kod + keyingi almashuvgacha soniyani qaytaradi (yoki frontend secret'dan hisoblaydi — lekin secret'ni faqat admin oladi). Xavfsizroq: server hisoblab beradi.
- **O'quvchi tomoni:** kirishda kod yuboriladi; server `totp.verify(code, valid_window=1)` bilan tekshiradi (oldingi/joriy oyna qabul qilinadi).
- **Nega ishonchli:** faqat admin ekranini ko'rayotgan xonadagi odam kodni biladi; imtihon faqat belgilangan vaqt oynasida `open`. Bu student auth o'rnini bosuvchi yengil himoya.

## 7. Import format spetsifikatsiyasi

### 7.1. Savollar — xlsx
| savol | variant_A | variant_B | variant_C | variant_D | togri_javob | mavzu |
|---|---|---|---|---|---|---|
| CPU nima? | Protsessor | Xotira | Disk | Monitor | A | Apparat |

- Birinchi qator sarlavha. `togri_javob`: A/B/C/D yoki 1–4. Bo'sh variantlar tashlab yuboriladi.

### 7.2. Savollar — docx (Faza 2)
```
1. CPU nima?
*a) Protsessor
b) Xotira
c) Disk
d) Monitor
```
`*` yoki `[x]` — to'g'ri javob belgisi.

### 7.3. O'quvchilar — xlsx / text
- xlsx: bitta ustun (`F.I.Sh`), har qatorda bitta ism.
- text: har qatorga bitta F.I.Sh.

### 7.4. Namunaviy fayllar
Admin panel har import turida "Namuna yuklab olish" beradi. Fayllar `backend/app/templates/samples/` da tayyor turadi (yoki dinamik generatsiya).

## 8. Baholash

- `percent = round(score / total * 100)`
- `grade` = `grading_scale` bo'yicha eng yuqori mos chegara (min'dan katta/teng bo'lgan birinchi harf)
- Default: A≥90, B 80–89, C 70–79, D 60–69, F<60 (kursga qarab sozlanadi)

## 9. Texnologiya steki

**Backend**
- FastAPI (Python 3.11+)
- SQLAlchemy 2.x + Alembic (migratsiya)
- PostgreSQL
- `python-jose` (JWT), `passlib[bcrypt]` (parol hash)
- `pyotp` (TOTP), `openpyxl` (xlsx), `python-docx` (docx)
- `pydantic-settings` (`.env` konfiguratsiya)

**Frontend**
- Vue 3 + Vite + TypeScript
- Vue Router, Pinia
- Yengil UI — og'ir komponent kutubxonasi yo'q (deadline uchun), oddiy CSS/utility

**Infratuzilma**
- Docker Compose: `backend`, `postgres`, `nginx`
- Nginx: `/api` → backend, qolgani → frontend statik build
- TLS: certbot (Let's Encrypt), `test.2007.uz`

## 10. Loyiha strukturasi

```
test-platform/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/            # SQLAlchemy modellar
│   │   ├── schemas/           # Pydantic sxemalar
│   │   ├── api/
│   │   │   ├── admin/         # kurs, guruh, savol, imtihon, natija, auth
│   │   │   └── exam/          # o'quvchi oqimi (public)
│   │   ├── services/          # import, totp, grading, exam-logic
│   │   ├── core/              # security (jwt, hashing)
│   │   └── templates/samples/ # namunaviy xlsx/docx
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/admin/       # login, kurslar, savollar, guruhlar, imtihonlar, natijalar, jonli-kod
│   │   ├── views/exam/        # kirish, parol, ism tanlash, test, natija
│   │   ├── components/
│   │   ├── stores/            # pinia
│   │   ├── router/
│   │   └── api/               # axios client
│   ├── Dockerfile
│   └── vite.config.ts
├── nginx/
│   └── default.conf
├── docker-compose.yml
├── .env.example
└── docs/
```

## 11. API (asosiy endpointlar)

**Admin (JWT talab qiladi)**
- `POST /api/admin/auth/login`
- `GET/POST/PUT/DELETE /api/admin/courses`
- `GET/POST/PUT/DELETE /api/admin/courses/{id}/questions`
- `POST /api/admin/courses/{id}/questions/import` (xlsx/docx)
- `GET /api/admin/samples/questions.xlsx` (namuna)
- `GET/POST/PUT/DELETE /api/admin/groups`
- `POST /api/admin/groups/{id}/students` (text/xlsx)
- `GET/POST/PUT/DELETE /api/admin/exams`
- `POST /api/admin/exams/{id}/status`
- `GET /api/admin/exams/{id}/totp` (jonli kod)
- `GET /api/admin/exams/{id}/results` (+ `/export` Faza 2)

**O'quvchi (public)**
- `GET /api/exam/{access_code}` (imtihon holati)
- `POST /api/exam/{access_code}/verify-code` (TOTP)
- `GET /api/exam/{access_code}/students` (band bo'lmaganlar)
- `POST /api/exam/{access_code}/start` (student_id → Attempt + savollar)
- `POST /api/exam/{access_code}/submit` (javoblar → natija)

## 12. Xavfsizlik va default qarorlar

- Admin — JWT, parol bcrypt. O'quvchi — auth yo'q, TOTP + vaqt oynasi.
- Savollar tasodifiy tortiladi + aralashtiriladi (ko'chirishga qarshi).
- To'g'ri javob (`correct_index`) o'quvchi API javoblarida **hech qachon** yuborilmaydi; baholash serverda.
- Attempt bir marta; `allow_resume` bilan boshqariladi.
- Soft-delete (`is_deleted`) — ma'lumot yo'qolmasin.

## 13. Yetkazib berish fazalari (bugun→ertaga: 3 fazani to'liq)

**Faza 1 — Yadro (MVP, ertagi imtihon uchun shart)**
- Modellar + Alembic migratsiya + Postgres ulanish
- Admin auth (login, JWT)
- Kurs CRUD + baholash shkalasi
- Savol: qo'lda kiritish + **xlsx import** + namuna xlsx
- Guruh CRUD + o'quvchi (text + xlsx) + namuna xlsx
- Imtihon yaratish (barcha sozlamalar + TOTP 4/6 · 30/60s)
- Jonli TOTP kod ekrani
- O'quvchi oqimi (kirish → parol → ism → test → topshirish)
- Avtomatik baholash + natija saqlash + o'quvchiga ko'rsatish
- **Lokal ishga tushirib to'liq sinash** (admin bir imtihon yaratadi, test topshiriladi)

**Faza 2 — To'liqlik**
- docx import + namuna docx
- Natijalar xlsx eksport
- Katta-ekran jonli kod rejimi (polish)
- Sozlamalar/tahrirlash UI to'ldirish
- **VPS diagnostikasi** (Docker/porti/resurs) → **deploy** (Docker Compose + Nginx + certbot, `test.2007.uz`)

**Faza 3 — Sayqal**
- Natijalar analitikasi (o'rtacha ball, taqsimot)
- Savol mavzular bo'yicha statistika
- Keyingi kurslar uchun test generatsiya oqimi (Oybek chatga qaytib topshiradi → to'g'ridan-to'g'ri bazaga qo'shish)

## 14. VPS deploy oldidan diagnostika (Faza 2 boshida bajariladi)

Contabo VPS'da (SSH orqali) tekshiriladi:
- `docker --version && docker compose version` — Docker bor-yo'qligi
- `df -h` — disk joyi
- `free -m` — xotira
- Ishlab turgan konteynerlar / portlar (`docker ps`, `ss -tlnp`) — 80/443 bandmi
- Nginx / boshqa reverse-proxy holati
- DNS: `test.2007.uz` A-record VPS IP'ga yo'naltirilganmi

Natijaga qarab: mavjud Nginx'ga qo'shamiz yoki konteynerdagi Nginx orqali.

## 15. Ochiq/keyinga qoldirilgan (YAGNI)

- Ko'p-adminlik, rollar tizimi — kerak emas
- Ko'p javobli / ochiq savollar — hozircha yo'q (Faza 3+ da ko'rib chiqiladi)
- Email/SMS bildirishnoma — yo'q
- Real-time monitoring (kim qayerda) — yo'q (Faza 3+)
