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
✅ **Faza 1 (yadro/MVP) — tugallangan.** Admin kurs/savol/guruh/o'quvchi/imtihon boshqaruvi, TOTP-himoyalangan o'quvchi oqimi, avtomatik baholash, natijalar jadvali — barchasi ishlaydi va pytest bilan qamrab olingan (76 test).

✅ **Faza 2 (deploy) — asosan tugallangan.** Docker Compose (backend + PostgreSQL) production'da ishlamoqda, Nginx + Let's Encrypt (certbot) orqali HTTPS yoqilgan. Asosiy domen (`2007.uz`) `.uz` registrida faollashtirilishini kutmoqda — hozircha `test.ibos.uz` subdomeni orqali ishlaydi.

⏳ **Qolgan Faza 2 ishlar:** docx savol importi, natijalarni xlsx'ga eksport qilish, sozlamalar UI'ni sayqallash.

⏳ **Faza 3:** natijalar analitikasi, mavzu bo'yicha statistika — hali boshlanmagan.

## Deploy

Production konfiguratsiyasi repo ichida: [`docker-compose.yml`](docker-compose.yml) (backend + PostgreSQL, `.env` orqali sirlar) va [`nginx/test-platform.conf`](nginx/test-platform.conf) (statik frontend + `/api` proxy). Birinchi marta deploy qilishda:

```bash
docker compose up -d --build
docker compose exec backend python scripts/create_admin.py --username <user> --password <parol>
certbot --nginx -d <domen>
```

## Xavfsizlik eslatmasi
`.env` hech qachon commit qilinmaydi (repo public). Admin paroli DB'da bcrypt-hash sifatida saqlanadi va `scripts/create_admin.py` CLI orqali o'rnatiladi; keyinchalik admin UI'dagi Profil sahifasidan o'zgartiriladi — hech qanday parol yoki maxfiy kalit kodda yoki git tarixida saqlanmaydi.
