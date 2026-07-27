# test-platform UI/UX Redizayn — Dizayn hujjati

## Maqsad

Hozirgi qo'lda yozilgan, generic flat CSS (`style.css`, hech qanday framework yo'q) ko'rinishini butunlay zamonaviy, izchil va foydalanuvchi uchun qulay (userFriendly) dizaynga almashtirish. Redizayn ham admin panelni, ham talaba tomonidagi imtihon oqimini qamrab oladi.

## Cheklovlar

- **Faqat frontend/vizual o'zgarish.** Backend API, route'lar, ma'lumotlar bazasi sxemasi o'zgarmaydi.
- Har bir sahifa/bosqich alohida commit qilinadi — loyiha har doim deploy qilishga tayyor holatda qolishi kerak (bu haqiqiy production'da ishlayotgan imtihon platformasi).
- Talaba tomonidagi imtihon oqimi (parol kiritish → ism tanlash → imtihon ekrani → natija) past quvvatli telefonlarda ham tez ishlashi va imtihon vaqtida chalg'itmasligi kerak — bu yerga og'ir komponentlar qo'yilmaydi.

## Vizual yo'nalish

Brauzer-asosida 4 ta uslub yo'nalishi taqdim etildi (Modern Minimal SaaS / Iliq-Do'stona / Korporativ-Rasmiy / Qorong'i-Texnologik). Foydalanuvchi A (Modern Minimal), C (Korporativ) va D (Qorong'i)ni yoqtirdi va ularni birlashtirishni so'radi. Natija tasdiqlangan:

- **Asosiy urg'u rang**: teal `#14b8a6` (kunduzgi rejim), `#2dd4bf` (tungi rejim)
- **Sidebar/qorong'i fon**: `#0f172a` (kunduzgi sidebar), `#020617` (tungi rejim fon)
- **Kontent foni**: `#f8fafc` (kunduzi), `#0f172a` (tunda)
- **Radius**: `10px` — barcha karta/tugma/input uchun izchil (A'ning yumshoqligi + C'ning "keskin" tuygusi orasidagi muvozanat)
- **Soya**: yumshoq, past-kontrast — `0 2px 8px rgba(15,23,42,0.08)` — elevatsiya orqali ierarxiya
- **Shrift**: mavjud tizim shrifti (`Segoe UI`, `system-ui` fallback) saqlanadi — tashqi CDN'dan shrift yuklanmaydi (tezlik va maxfiylik uchun); tipografiya shkalasi (h1-h3, kichik/katta matn o'lchamlari) aniqroq belgilanadi.
- **Tungi rejim**: standart holatda `prefers-color-scheme` ga qarab avtomatik tanlanadi, qo'lda almashtirish tugmasi mavjud, tanlov `localStorage`da saqlanadi.

## Komponent kutubxonasi: Naive UI

Naive UI va PrimeVue solishtirildi. Naive UI tanlandi, sabablari:

| Mezon | Naive UI | PrimeVue |
|---|---|---|
| Branding moslash | `themeOverrides` obyekti orqali har bir token aniq belgilanadi | Yangi preset tizimi ham yaxshi, lekin ko'proq qatlam (unstyled mode, PassThrough) |
| Tungi rejim | `darkTheme` + `themeOverrides` — bitta joyda | CSS-o'zgaruvchi + `.dark` klass, ko'proq qo'lda sozlash |
| Bundle hajmi | To'liq tree-shakeable | Tree-shakeable, lekin Tailwind'ga bog'liqlik ortmoqda |
| TypeScript | TS-first yozilgan | TS qo'llab-quvvatlaydi, Vue2 merosi bor |
| Jadval ehtiyoji | `n-data-table` yetarli (jadvallar kichik, ~20-100 qator) | `DataTable` ko'proq funksiyali, lekin bizga ortiqcha |

Integratsiya: `theme.ts` faylida yagona `themeOverrides` obyekti yaratiladi (yuqoridagi ranglar/radius bilan), `n-config-provider` orqali `App.vue`da o'ralib qo'yiladi. Mavjud qo'lda yozilgan `.btn`, `.card`, `.form-group` klasslari bosqichma-bosqich `n-button`, `n-card`, `n-input`, `n-data-table`, `n-modal` va h.k.ga almashtiriladi.

## Qamrov va sahifalar

**Admin panel** (to'liq Naive UI komponentlari bilan):
- `AdminLayout` — sidebar navigatsiya, tungi rejim tugmasi
- `LoginView`, `ProfileView`
- `CoursesView`, `QuestionsView`, `QuestionForm` (modal → `n-modal`)
- `GroupsView`, `StudentImport`, `ImportDialog`
- `ExamsView`, `ExamFormView`, `LiveCodeView` (TOTP kod — katta/aniq ko'rinish muhim)
- `ResultsView` — jadval `n-data-table`ga o'tadi

**Talaba tomoni** (yengil variant — faqat `n-button`/`n-radio` kabi yengil elementlar, og'ir komponentlar yo'q):
- `PasswordView`, `PickNameView`, `ExamEntryView`, `ExamView`, `ResultView`

Vaqt-taymer va savol-kartalar joylashuvi funksional jihatdan deyarli hozirgidek qoladi, faqat yangi rang/tipografiya/radius tokenlari qo'llaniladi.

## Joriy qilish tartibi (har biri alohida commit)

1. `theme.ts` yaratish + Naive UI o'rnatish + `AdminLayout` yangilash (poydevor)
2. Admin sahifalar birma-bir: Courses → Questions → Groups → Exams → LiveCode → Results → Profile
3. Talaba oqimi (5 sahifa, yengil variant)
4. Yakuniy tozalash: eski `.btn`/`.card`/`.form-group` qoldiqlarini `style.css`dan olib tashlash

## Test/tekshirish yondashuvi

Frontend uchun mavjud avtomatik test to'plami yo'q (faqat backend'da pytest bor, 81 test). Bu vizual redizayn bo'lgani uchun avtomatik vizual-regression test qo'shish YAGNI — buning o'rniga har bir sahifa commit qilingandan keyin brauzerda qo'lda tekshiriladi (asosiy oqim + edge case'lar, mavjud loyiha konventsiyasiga mos — masalan modal/width tuzatishlarida qilingani kabi).

## Qamrovdan tashqari

- Backend API/route o'zgarishlari
- Avtomatik frontend test infratuzilmasini qo'shish
- `test.2007.uz` domenini faollashtirish (alohida, kutilayotgan masala)
