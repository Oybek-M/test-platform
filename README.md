# test-platform

Kompyuter savodxonligi (va keyingi kurslar) uchun dinamik onlayn imtihon/test platformasi.

- **Admin** kurs, savol bazasi, guruh, o'quvchilar va imtihonlarni boshqaradi.
- **O'quvchilar** auth'siz — ro'yxatdan ism tanlab, rotatsion parol (TOTP) bilan kirib test topshiradi.
- Natija avtomatik baholanadi (foiz → sozlanadigan harf baho: A/B/C/D/F).

## Texnologiya
- **Backend:** FastAPI + PostgreSQL (SQLAlchemy, Alembic), pyotp, openpyxl, python-docx
- **Frontend:** Vue 3 + Vite + TypeScript (Pinia, Vue Router)
- **Deploy:** Docker Compose + Nginx + certbot

## Hujjatlar
- Dizayn (spec): [docs/2026-07-23-test-platform-design.md](docs/2026-07-23-test-platform-design.md)
- Implementation plan: [docs/2026-07-23-test-platform-plan.md](docs/2026-07-23-test-platform-plan.md)

## Holat
🚧 Ishlab chiqilmoqda — Faza 1 (yadro/MVP).

## Xavfsizlik eslatmasi
`.env` hech qachon commit qilinmaydi. Admin paroli DB'da bcrypt-hash sifatida saqlanadi va `scripts/create_admin.py` CLI orqali o'rnatiladi — repo public bo'lganda ham hech qanday sir sizib chiqmaydi.
