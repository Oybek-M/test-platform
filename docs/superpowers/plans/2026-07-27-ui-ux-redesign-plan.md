# test-platform UI/UX Redizayn Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redizayn qil test-platform frontend'ini (admin panel + talaba imtihon oqimi) Naive UI komponent kutubxonasi va teal/shifer vizual identifikatsiya asosida, `docs/superpowers/specs/2026-07-27-ui-ux-redesign-design.md` bo'yicha.

**Architecture:** Naive UI `n-config-provider` orqali global `themeOverrides` bilan o'ralgan Vue 3 ilova. Sidebar doim to'q (nested `n-config-provider :theme="darkTheme"`), sahifa foni `prefers-color-scheme`ga qarab avtomatik yoki qo'lda almashtiriladigan tungi/kunduzgi rejim. Router marshrutlari lazy-loading (`() => import(...)`) ga o'tkaziladi — bu talaba-oqimi sahifalarini admin-panel komponentlaridan (masalan `n-data-table`) alohida JS chunk'ga ajratadi, natijada past quvvatli telefonlarda talaba-oqimi tezroq yuklanadi.

**Tech Stack:** Vue 3 + TypeScript, Naive UI, `unplugin-vue-components` + `unplugin-auto-import` (avtomatik komponent/composable import), Vite, mavjud Pinia store'lar va Axios client o'zgarishsiz qoladi.

**Muhim izoh — test yondashuvi:** Bu loyihada frontend uchun avtomatik test to'plami yo'q (faqat backend'da pytest bor). Dizayn hujjatida (spec) kelishilganidek, har bir vazifadan keyingi tekshiruv "yozib-testni ishga tushirish" o'rniga **`npm run build` (vue-tsc tip-tekshiruvi) + brauzerda qo'lda tekshirish** shaklida bo'ladi. Har bir vazifa quyidagi ikki tekshiruvni o'z ichiga oladi: (1) build toza o'tishi, (2) brauzerda aniq ko'rsatilgan qadamlar bo'yicha tekshirish.

**Muhim izoh — Naive UI konventsiyalari (barcha vazifalarda takrorlanadi):**
- Xatolik xabarlari: mahalliy `error` ref o'rniga `useMessage()`dan `message.error(...)` (avtomatik import qilingan, alohida `import` kerak emas)
- Muvaffaqiyat xabarlari: `message.success(...)`
- `confirm()` o'rniga: `useDialog()`dan `dialog.warning({ title, content, positiveText, negativeText, onPositiveClick })` (avtomatik import qilingan)
- `.card` → `<n-card>`, `.btn` → `<n-button>` (`type="primary"` asosiy, `type="error"` xavfli, `secondary`/`quaternary`/`dashed` ikkinchi darajali), `.form-group` → `<n-form-item>` + `<n-input>`/`<n-input-number>`/`<n-select>`/`<n-checkbox>`/`<n-date-picker>`
- Jadvallar: kichik/sodda ro'yxatlar uchun `<n-table>`, harakat tugmalari va murakkabroq ustunlar kerak bo'lganda `<n-data-table :columns :data>` (`h()` render funksiyalari bilan)

---

### Task 1: Naive UI poydevori — o'rnatish, tema, tungi rejim, lazy-loading router

**Files:**
- Modify: `frontend/package.json` (dependency qo'shiladi — `npm install` orqali)
- Modify: `frontend/vite.config.ts`
- Create: `frontend/src/theme.ts`
- Create: `frontend/src/composables/useDarkMode.ts`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `.gitignore` (repo ildizida)

- [ ] **Step 1: Paketlarni o'rnatish**

Run: `cd frontend && npm install naive-ui unplugin-vue-components unplugin-auto-import`

Expected: `package.json`ning `dependencies`iga `naive-ui`, `devDependencies`iga `unplugin-vue-components` va `unplugin-auto-import` qo'shiladi.

- [ ] **Step 2: `vite.config.ts`ni yangilash**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: [{ 'naive-ui': ['useDialog', 'useMessage', 'useNotification', 'useLoadingBar'] }],
    }),
    Components({
      resolvers: [NaiveUiResolver()],
    }),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

Bu `<n-button>`, `<n-card>` kabi komponentlarni har bir faylda `import` qilmasdan ishlatish, hamda `useMessage()`/`useDialog()`ni avtomatik import qilish imkonini beradi.

- [ ] **Step 3: `theme.ts` yaratish**

```typescript
import type { GlobalThemeOverrides } from 'naive-ui'

export const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#14b8a6',
    primaryColorHover: '#0d9488',
    primaryColorPressed: '#0f766e',
    primaryColorSuppl: '#14b8a6',
    borderRadius: '10px',
    bodyColor: '#f8fafc',
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
  },
}

export const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#2dd4bf',
    primaryColorHover: '#5eead4',
    primaryColorPressed: '#14b8a6',
    primaryColorSuppl: '#2dd4bf',
    borderRadius: '10px',
    bodyColor: '#0f172a',
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
  },
}
```

Bu tokenlar loyihaning tasdiqlangan vizual yo'nalishiga mos (teal urg'u, 10px radius). `common.bodyColor` `<n-global-style>` orqali sahifa foniga qo'llaniladi.

- [ ] **Step 4: `composables/useDarkMode.ts` yaratish**

```typescript
import { ref, watch } from 'vue'
import { useOsTheme } from 'naive-ui'

const STORAGE_KEY = 'test-platform-theme'
const osTheme = useOsTheme()

function getInitialValue(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'dark') return true
  if (stored === 'light') return false
  return osTheme.value === 'dark'
}

const isDark = ref(getInitialValue())

watch(isDark, (value) => {
  localStorage.setItem(STORAGE_KEY, value ? 'dark' : 'light')
})

export function useDarkMode() {
  function toggle() {
    isDark.value = !isDark.value
  }
  return { isDark, toggle }
}
```

`isDark` modul darajasida (singleton) saqlanadi — barcha komponentlar bitta holatni ulashadi, alohida Pinia store shart emas (bitta boolean uchun ortiqcha bo'lardi).

- [ ] **Step 5: `App.vue`ni yangilash**

```vue
<script setup lang="ts">
import { darkTheme } from 'naive-ui'
import { useDarkMode } from './composables/useDarkMode'
import { lightThemeOverrides, darkThemeOverrides } from './theme'

const { isDark } = useDarkMode()
</script>

<template>
  <n-config-provider
    :theme="isDark ? darkTheme : null"
    :theme-overrides="isDark ? darkThemeOverrides : lightThemeOverrides"
  >
    <n-global-style />
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
```

- [ ] **Step 6: `router/index.ts`ni lazy-loading'ga o'tkazish**

Talaba-oqimi sahifalari (`/e/:accessCode/...`) admin-panelning og'ir komponentlarini (masalan `n-data-table`) o'z JS bog'lamiga tortmasligi uchun barcha route komponentlari dinamik import qilinadi:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const LoginView = () => import('../views/admin/LoginView.vue')
const ProfileView = () => import('../views/admin/ProfileView.vue')
const CoursesView = () => import('../views/admin/CoursesView.vue')
const QuestionsView = () => import('../views/admin/QuestionsView.vue')
const GroupsView = () => import('../views/admin/GroupsView.vue')
const ExamsView = () => import('../views/admin/ExamsView.vue')
const ExamFormView = () => import('../views/admin/ExamFormView.vue')
const LiveCodeView = () => import('../views/admin/LiveCodeView.vue')
const ResultsView = () => import('../views/admin/ResultsView.vue')
const AdminLayout = () => import('../components/AdminLayout.vue')
const ExamEntryView = () => import('../views/exam/ExamEntryView.vue')
const PasswordView = () => import('../views/exam/PasswordView.vue')
const PickNameView = () => import('../views/exam/PickNameView.vue')
const ExamView = () => import('../views/exam/ExamView.vue')
const ResultView = () => import('../views/exam/ResultView.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/admin' },
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/courses' },
        { path: 'profile', name: 'admin-profile', component: ProfileView },
        { path: 'courses', name: 'admin-courses', component: CoursesView },
        { path: 'courses/:courseId/questions', name: 'admin-questions', component: QuestionsView },
        { path: 'groups', name: 'admin-groups', component: GroupsView },
        { path: 'exams', name: 'admin-exams', component: ExamsView },
        { path: 'exams/new', name: 'admin-exam-new', component: ExamFormView },
        { path: 'exams/:id/live-code', name: 'admin-exam-live-code', component: LiveCodeView },
        { path: 'exams/:id/results', name: 'admin-exam-results', component: ResultsView },
      ],
    },
    {
      path: '/e/:accessCode',
      children: [
        { path: '', name: 'exam-entry', component: ExamEntryView },
        { path: 'password', name: 'exam-password', component: PasswordView },
        { path: 'name', name: 'exam-name', component: PickNameView },
        { path: 'test', name: 'exam-test', component: ExamView },
        { path: 'result', name: 'exam-result', component: ResultView },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return { name: 'login' }
  }
  return true
})

export default router
```

- [ ] **Step 7: `.gitignore`ga generatsiya qilinadigan fayllarni qo'shish**

Repo ildizidagi `.gitignore`da `# --- Node / Vue (frontend) ---` bo'limiga qo'shing:

```
frontend/auto-imports.d.ts
frontend/components.d.ts
```

- [ ] **Step 8: Build orqali tekshirish**

Run: `cd frontend && npm run build`

Expected: xatosiz build, `dist/assets/*.js` fayli generatsiya bo'ladi. Xato chiqsa — theme.ts'dagi token nomlarini yoki import yo'llarini tekshiring.

- [ ] **Step 9: Brauzerda qo'lda tekshirish**

Run: `cd frontend && npm run dev`, brauzerda `http://localhost:5173/login` oching.

Tekshiring:
1. Sahifa xatosiz yuklanadi (konsolda qizil xato yo'q)
2. Brauzer konsolida ishga tushiring: `localStorage.setItem('test-platform-theme', 'dark'); location.reload()`
3. Qayta yuklangandan keyin: `getComputedStyle(document.body).backgroundColor` → `"rgb(15, 23, 42)"` qaytarishi kerak (tungi rejim foni)
4. `localStorage.setItem('test-platform-theme', 'light'); location.reload()` — fon qayta och rangga qaytishi kerak

- [ ] **Step 10: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/src/theme.ts frontend/src/composables/useDarkMode.ts frontend/src/App.vue frontend/src/router/index.ts .gitignore
git commit -m "feat: Naive UI poydevori + tema tokenlari + tungi rejim + lazy-loading router"
```

---

### Task 2: AdminLayout redizayni

**Files:**
- Modify: `frontend/src/components/AdminLayout.vue`

- [ ] **Step 1: To'liq faylni almashtirish**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { darkTheme } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { useDarkMode } from '../composables/useDarkMode'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { isDark, toggle } = useDarkMode()

const menuOptions = [
  { label: 'Kurslar', key: 'admin-courses' },
  { label: 'Guruhlar', key: 'admin-groups' },
  { label: 'Imtihonlar', key: 'admin-exams' },
  { label: 'Profil', key: 'admin-profile' },
]

const activeKey = computed(() => {
  const name = String(route.name || '')
  if (name.startsWith('admin-exam')) return 'admin-exams'
  if (name === 'admin-questions') return 'admin-courses'
  return name
})

function handleMenuSelect(key: string) {
  router.push({ name: key })
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <n-layout has-sider style="min-height: 100vh;">
    <n-layout-sider
      bordered
      width="220"
      content-style="padding: 1.25rem 1rem; display: flex; flex-direction: column; min-height: 100vh; background: #0f172a;"
    >
      <n-config-provider :theme="darkTheme">
        <h3 style="margin: 0 0 1.5rem 0; color: #fff;">test-platform</h3>
        <n-menu :value="activeKey" :options="menuOptions" @update:value="handleMenuSelect" />
        <div style="margin-top: auto; display: flex; flex-direction: column; gap: 0.5rem; padding-top: 1.5rem;">
          <n-button quaternary style="justify-content: flex-start;" @click="toggle">
            {{ isDark ? '☀ Kunduzgi rejim' : '🌙 Tungi rejim' }}
          </n-button>
          <n-button secondary @click="logout">Chiqish</n-button>
        </div>
      </n-config-provider>
    </n-layout-sider>
    <n-layout-content content-style="padding: 1.5rem;">
      <div style="max-width: 1100px; margin: 0 auto;">
        <router-view />
      </div>
    </n-layout-content>
  </n-layout>
</template>
```

Nested `<n-config-provider :theme="darkTheme">` sidebar ichidagi barcha komponentlarni (menu, tugmalar, matn) doimiy ravishda to'q fon ustida to'g'ri kontrastda ko'rsatadi — bu ilovaning umumiy kunduzgi/tungi rejimidan mustaqil, chunki sidebar har doim to'q bo'lishi kerak (dizayn hujjatiga ko'ra).

- [ ] **Step 2: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 3: Brauzerda qo'lda tekshirish**

`npm run dev`, admin sifatida kiring (`/login`). Tekshiring:
1. Sidebar to'q shifer rangda (`#0f172a`), matn oq/o'qilishi oson
2. Joriy sahifaga mos menyu punkti teal rang bilan ajralib turadi
3. "Tungi rejim" tugmasini bosganda butun sahifa foni to'q rangga o'tadi, tugma matni "Kunduzgi rejim"ga o'zgaradi
4. "Chiqish" tugmasi `/login`ga yo'naltiradi

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/AdminLayout.vue
git commit -m "feat: AdminLayout'ni Naive UI bilan qayta dizayn qilish"
```

---

### Task 3: CoursesView redizayni

**Files:**
- Modify: `frontend/src/views/admin/CoursesView.vue`

- [ ] **Step 1: To'liq faylni almashtirish**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listCourses, createCourse, updateCourse, deleteCourse, type Course, type GradeBand } from '../../api/courses'

const message = useMessage()
const dialog = useDialog()

const courses = ref<Course[]>([])
const loading = ref(false)

const newName = ref('')
const newDescription = ref('')

const editingScaleId = ref<number | null>(null)
const editingScale = ref<GradeBand[]>([])

async function load() {
  loading.value = true
  try {
    courses.value = await listCourses()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Kurslarni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function addCourse() {
  if (!newName.value.trim()) return
  try {
    await createCourse({ name: newName.value, description: newDescription.value || undefined })
    newName.value = ''
    newDescription.value = ''
    message.success("Kurs qo'shildi")
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Kurs yaratib bo'lmadi")
  }
}

function confirmRemoveCourse(course: Course) {
  dialog.warning({
    title: "Kursni o'chirish",
    content: `"${course.name}" kursini o'chirishni tasdiqlaysizmi?`,
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      await deleteCourse(course.id)
      message.success("Kurs o'chirildi")
      await load()
    },
  })
}

function startEditScale(course: Course) {
  editingScaleId.value = course.id
  editingScale.value = course.grading_scale.map((b) => ({ ...b }))
}

function addBand() {
  editingScale.value.push({ grade: '', min: 0 })
}

function removeBand(index: number) {
  editingScale.value.splice(index, 1)
}

async function saveScale(courseId: number) {
  try {
    await updateCourse(courseId, { grading_scale: editingScale.value })
    editingScaleId.value = null
    message.success('Shkala saqlandi')
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Shkalani saqlab bo'lmadi")
  }
}
</script>

<template>
  <div>
    <h2>Kurslar</h2>

    <n-card title="Yangi kurs" style="margin-bottom: 1rem;">
      <n-space align="end">
        <n-form-item label="Nomi" style="margin-bottom: 0;">
          <n-input v-model:value="newName" placeholder="Kurs nomi" />
        </n-form-item>
        <n-form-item label="Tavsif" style="margin-bottom: 0;">
          <n-input v-model:value="newDescription" placeholder="Ixtiyoriy" />
        </n-form-item>
        <n-button type="primary" @click="addCourse">Qo'shish</n-button>
      </n-space>
    </n-card>

    <n-spin :show="loading">
      <n-card v-for="course in courses" :key="course.id" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div>
            <h3 style="margin: 0;">{{ course.name }}</h3>
            <p v-if="course.description" class="muted" style="margin: 0.25rem 0 0 0;">{{ course.description }}</p>
          </div>
          <n-space>
            <router-link :to="`/admin/courses/${course.id}/questions`">
              <n-button secondary>Savollar</n-button>
            </router-link>
            <n-button secondary @click="startEditScale(course)">Baholash shkalasi</n-button>
            <n-button type="error" secondary @click="confirmRemoveCourse(course)">O'chirish</n-button>
          </n-space>
        </div>

        <div v-if="editingScaleId === course.id" style="margin-top: 1rem; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 1rem;">
          <n-space v-for="(band, i) in editingScale" :key="i" align="center" style="margin-bottom: 0.5rem;">
            <n-input v-model:value="band.grade" placeholder="Baho (A)" style="width: 100px;" />
            <n-input-number v-model:value="band.min" :min="0" :max="100" placeholder="Min %" style="width: 120px;" />
            <n-button type="error" quaternary @click="removeBand(i)">X</n-button>
          </n-space>
          <n-space>
            <n-button dashed @click="addBand">+ Daraja qo'shish</n-button>
            <n-button type="primary" @click="saveScale(course.id)">Saqlash</n-button>
            <n-button @click="editingScaleId = null">Bekor qilish</n-button>
          </n-space>
        </div>
        <p v-else class="muted" style="margin: 0.75rem 0 0 0;">
          Shkala: {{ course.grading_scale.map(b => `${b.grade}≥${b.min}`).join(' · ') }}
        </p>
      </n-card>

      <n-empty v-if="!loading && courses.length === 0" description="Hozircha kurslar yo'q" />
    </n-spin>
  </div>
</template>
```

- [ ] **Step 2: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 3: Brauzerda qo'lda tekshirish**

`/admin/courses`ga o'ting. Tekshiring:
1. Yangi kurs qo'shish ishlaydi, muvaffaqiyat toast'i chiqadi
2. "Baholash shkalasi" tugmasi shkala tahrirlash blokini ochadi, saqlash ishlaydi
3. "O'chirish" tugmasi tasdiqlash dialogini ko'rsatadi, tasdiqlagandan keyin kurs ro'yxatdan yo'qoladi
4. Kurslar bo'sh bo'lsa "Hozircha kurslar yo'q" ko'rinadi

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/admin/CoursesView.vue
git commit -m "feat: CoursesView'ni Naive UI bilan qayta dizayn qilish"
```

---

### Task 4: QuestionsView + QuestionForm + Modal → n-modal

**Files:**
- Modify: `frontend/src/views/admin/QuestionsView.vue`
- Modify: `frontend/src/components/QuestionForm.vue`
- Modify: `frontend/src/components/ImportDialog.vue`
- Delete: `frontend/src/components/Modal.vue` (endi `n-modal` ishlatiladi)

- [ ] **Step 1: `QuestionForm.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  initial?: { text: string; options: string[]; correct_index: number; topic: string | null }
}>()
const emit = defineEmits<{
  submit: [payload: { text: string; options: string[]; correct_index: number; topic?: string }]
  cancel: []
}>()

const text = ref(props.initial?.text || '')
const options = ref<string[]>(props.initial?.options ? [...props.initial.options] : ['', ''])
const correctIndex = ref(props.initial?.correct_index ?? 0)
const topic = ref(props.initial?.topic || '')

function addOption() {
  if (options.value.length < 6) options.value.push('')
}

function removeOption(i: number) {
  if (options.value.length > 2) {
    options.value.splice(i, 1)
    if (correctIndex.value >= options.value.length) {
      correctIndex.value = options.value.length - 1
    }
  }
}

function submit() {
  emit('submit', {
    text: text.value,
    options: options.value.filter((o) => o.trim() !== ''),
    correct_index: correctIndex.value,
    topic: topic.value || undefined,
  })
}
</script>

<template>
  <n-form :label-width="0">
    <n-form-item label="Savol matni">
      <n-input v-model:value="text" type="textarea" :rows="2" />
    </n-form-item>
    <n-form-item label="Variantlar (to'g'ri javobni belgilang)">
      <div style="width: 100%;">
        <n-space v-for="(_, i) in options" :key="i" align="center" style="margin-bottom: 0.5rem; width: 100%;">
          <input type="radio" name="correct-option" :checked="correctIndex === i" @change="correctIndex = i" />
          <n-input v-model:value="options[i]" :placeholder="`Variant ${i + 1}`" style="flex: 1;" />
          <n-button v-if="options.length > 2" type="error" quaternary @click="removeOption(i)">X</n-button>
        </n-space>
        <n-button v-if="options.length < 6" dashed @click="addOption">+ Variant qo'shish</n-button>
      </div>
    </n-form-item>
    <n-form-item label="Mavzu (ixtiyoriy)">
      <n-input v-model:value="topic" />
    </n-form-item>
    <n-space>
      <n-button type="primary" @click="submit">Saqlash</n-button>
      <n-button @click="emit('cancel')">Bekor qilish</n-button>
    </n-space>
  </n-form>
</template>
```

Eslatma: bu yerda `<n-space>` `width: 100%` bilan flex konteyner sifatida ishlatilgani uchun eski "23px'ga siqilib qolgan input" bugi butunlay yo'qoladi — `n-input`ning o'zi `flex: 1`ni to'g'ri qo'llab-quvvatlaydi.

- [ ] **Step 2: `QuestionsView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue'
import { useRoute } from 'vue-router'
import type { DataTableColumns } from 'naive-ui'
import { NButton } from 'naive-ui'
import {
  listQuestions,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  type Question,
} from '../../api/questions'
import QuestionForm from '../../components/QuestionForm.vue'
import ImportDialog from '../../components/ImportDialog.vue'

const route = useRoute()
const courseId = computed(() => Number(route.params.courseId))
const message = useMessage()
const dialog = useDialog()

const questions = ref<Question[]>([])
const loading = ref(false)

const topicFilter = ref('')
const showForm = ref(false)
const showImport = ref(false)
const editingQuestion = ref<Question | null>(null)

async function load() {
  loading.value = true
  try {
    questions.value = await listQuestions(courseId.value, {
      topic: topicFilter.value || undefined,
    })
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Savollarni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

onMounted(load)

function openCreateForm() {
  editingQuestion.value = null
  showForm.value = true
}

function openEditForm(q: Question) {
  editingQuestion.value = q
  showForm.value = true
}

async function handleSubmit(payload: { text: string; options: string[]; correct_index: number; topic?: string }) {
  try {
    if (editingQuestion.value) {
      await updateQuestion(courseId.value, editingQuestion.value.id, payload)
    } else {
      await createQuestion(courseId.value, payload)
    }
    showForm.value = false
    editingQuestion.value = null
    message.success('Savol saqlandi')
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Savolni saqlab bo'lmadi")
  }
}

async function toggleActive(q: Question) {
  await updateQuestion(courseId.value, q.id, { is_active: !q.is_active })
  await load()
}

function confirmRemove(q: Question) {
  dialog.warning({
    title: "Savolni o'chirish",
    content: "Savolni o'chirishni tasdiqlaysizmi?",
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      await deleteQuestion(courseId.value, q.id)
      message.success("Savol o'chirildi")
      await load()
    },
  })
}

function onImported() {
  showImport.value = false
  load()
}

const columns: DataTableColumns<Question> = [
  { title: 'Savol', key: 'text' },
  {
    title: 'Variantlar',
    key: 'options',
    render(row) {
      return row.options
        .map((opt, i) => (i === row.correct_index ? `✓ ${opt}` : opt))
        .join(', ')
    },
  },
  { title: 'Mavzu', key: 'topic', render: (row) => row.topic || '-' },
  {
    title: 'Faol',
    key: 'is_active',
    render(row) {
      return h('input', {
        type: 'checkbox',
        checked: row.is_active,
        onChange: () => toggleActive(row),
      })
    },
  },
  {
    title: '',
    key: 'actions',
    render(row) {
      return h('div', { style: 'display: flex; gap: 0.5rem;' }, [
        h(NButton, { secondary: true, onClick: () => openEditForm(row) }, { default: () => 'Tahrirlash' }),
        h(NButton, { type: 'error', secondary: true, onClick: () => confirmRemove(row) }, { default: () => "O'chirish" }),
      ])
    },
  },
]
</script>

<template>
  <div>
    <router-link to="/admin/courses" class="muted">&larr; Kurslarga qaytish</router-link>
    <h2>Savollar</h2>

    <n-space align="end" style="margin-bottom: 1rem;">
      <n-form-item label="Mavzu bo'yicha filtr" style="margin-bottom: 0;">
        <n-input v-model:value="topicFilter" placeholder="Mavzu..." @keyup.enter="load" />
      </n-form-item>
      <n-button type="primary" @click="openCreateForm">+ Yangi savol</n-button>
      <n-button secondary @click="showImport = !showImport">Xlsx import</n-button>
    </n-space>

    <ImportDialog v-if="showImport" :course-id="courseId" @imported="onImported" @close="showImport = false" />

    <n-modal v-model:show="showForm" preset="card" :title="editingQuestion ? 'Savolni tahrirlash' : 'Yangi savol'" style="max-width: 640px;">
      <QuestionForm
        :initial="editingQuestion || undefined"
        @submit="handleSubmit"
        @cancel="showForm = false"
      />
    </n-modal>

    <n-data-table :columns="columns" :data="questions" :loading="loading" :bordered="false" />
    <n-empty v-if="!loading && questions.length === 0" description="Hozircha savollar yo'q" style="margin-top: 1rem;" />
  </div>
</template>
```

Muhim izoh: `unplugin-vue-components` faqat **shablon (`<template>`)**dagi `<n-button>` kabi teglarni avtomatik tanib import qiladi — `render`/`h()` funksiyalari ichida bu ishlamaydi, shuning uchun `NButton` yuqorida qo'lda import qilingan va `h(NButton, ...)` shaklida ishlatilgan.

- [ ] **Step 3: `ImportDialog.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { importQuestions, sampleQuestionsUrl, type QuestionImportPreview } from '../api/questions'

const props = defineProps<{ courseId: number }>()
const emit = defineEmits<{ imported: []; close: [] }>()
const message = useMessage()

const file = ref<File | null>(null)
const preview = ref<QuestionImportPreview | null>(null)
const errors = ref<string[]>([])
const loading = ref(false)

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  file.value = target.files?.[0] || null
  preview.value = null
  errors.value = []
}

async function doPreview() {
  if (!file.value) return
  loading.value = true
  errors.value = []
  try {
    const result = await importQuestions(props.courseId, file.value, false)
    preview.value = result as QuestionImportPreview
  } catch (e: any) {
    if (e?.response?.status === 422 && e.response.data?.detail) {
      errors.value = e.response.data.detail.errors || []
      message.error(`Faylda ${errors.value.length} ta xato topildi. Tuzatib qayta yuklang.`)
    } else {
      message.error("Faylni tahlil qilib bo'lmadi")
    }
  } finally {
    loading.value = false
  }
}

async function doConfirm() {
  if (!file.value) return
  loading.value = true
  try {
    await importQuestions(props.courseId, file.value, true)
    message.success('Savollar import qilindi')
    emit('imported')
  } catch (e: any) {
    message.error(e?.response?.data?.detail?.errors?.join(', ') || "Import qilib bo'lmadi")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <n-card title="Xlsx orqali savol import qilish" style="margin-bottom: 1rem;">
    <p><a :href="sampleQuestionsUrl()" target="_blank">Namuna faylni yuklab olish</a></p>
    <input type="file" accept=".xlsx" @change="onFileChange" />
    <n-alert v-if="errors.length" type="error" style="margin-top: 1rem;">
      <ul style="margin: 0; padding-left: 1.2rem;">
        <li v-for="(err, i) in errors" :key="i">{{ err }}</li>
      </ul>
    </n-alert>
    <n-alert v-if="preview" type="success" style="margin-top: 1rem;">
      {{ preview.questions_found }} ta savol topildi. Tasdiqlab importni yakunlang.
    </n-alert>
    <n-space style="margin-top: 1rem;">
      <n-button secondary :disabled="!file || loading" :loading="loading" @click="doPreview">
        Ko'rib chiqish
      </n-button>
      <n-button type="primary" :disabled="!preview || loading" @click="doConfirm">
        Tasdiqlash va import qilish
      </n-button>
      <n-button @click="emit('close')">Yopish</n-button>
    </n-space>
  </n-card>
</template>
```

- [ ] **Step 4: `Modal.vue`ni o'chirish**

Run: `rm frontend/src/components/Modal.vue`

`grep -rn "components/Modal" frontend/src` orqali boshqa hech qanday faylda ishlatilmasligini tasdiqlang (faqat `QuestionsView.vue`da ishlatilgan edi, u Step 2'da `n-modal`ga o'tkazildi).

- [ ] **Step 5: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak. `NButton` importi haqidagi eslatmaga alohida e'tibor bering — build xatosi shu joyda chiqishi mumkin.

- [ ] **Step 6: Brauzerda qo'lda tekshirish**

`/admin/courses/<id>/questions`ga o'ting. Tekshiring:
1. "Yangi savol" tugmasi modalni ochadi, variant inputlari to'liq kenglikda ko'rinadi (eski 23px bug yo'q)
2. Ro'yxatdagi savolni "Tahrirlash" bosganda modal ochiladi, sahifa scroll pozitsiyasi o'zgarmaydi
3. To'g'ri javob jadvalda `✓` belgisi bilan ko'rinadi
4. Xlsx import: fayl tanlash → ko'rib chiqish → tasdiqlash oqimi ishlaydi
5. "O'chirish" tasdiqlash dialogini ko'rsatadi

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/admin/QuestionsView.vue frontend/src/components/QuestionForm.vue frontend/src/components/ImportDialog.vue
git rm frontend/src/components/Modal.vue
git commit -m "feat: QuestionsView/QuestionForm/ImportDialog'ni Naive UI bilan qayta dizayn qilish"
```

---

### Task 5: GroupsView + StudentImport

**Files:**
- Modify: `frontend/src/views/admin/GroupsView.vue`
- Modify: `frontend/src/components/StudentImport.vue`

- [ ] **Step 1: `StudentImport.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { addStudentsFromText, addStudentsFromXlsx, sampleStudentsUrl } from '../api/groups'

const props = defineProps<{ groupId: number }>()
const emit = defineEmits<{ imported: [] }>()
const message = useMessage()

const textInput = ref('')
const file = ref<File | null>(null)
const loading = ref(false)

function onFileChange(e: Event) {
  file.value = (e.target as HTMLInputElement).files?.[0] || null
}

async function submitText() {
  if (!textInput.value.trim()) return
  loading.value = true
  try {
    const result = await addStudentsFromText(props.groupId, textInput.value)
    if (result.warnings.length) {
      message.warning(result.warnings.join('; '))
    } else {
      message.success("O'quvchilar qo'shildi")
    }
    textInput.value = ''
    emit('imported')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "O'quvchilarni qo'shib bo'lmadi")
  } finally {
    loading.value = false
  }
}

async function submitXlsx() {
  if (!file.value) return
  loading.value = true
  try {
    const result = await addStudentsFromXlsx(props.groupId, file.value)
    if (result.warnings.length) {
      message.warning(result.warnings.join('; '))
    } else {
      message.success("O'quvchilar qo'shildi")
    }
    file.value = null
    emit('imported')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Faylni import qilib bo'lmadi")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h4>O'quvchi qo'shish</h4>
    <n-form-item label="Har qatorga bitta F.I.Sh">
      <n-input
        v-model:value="textInput"
        type="textarea"
        :rows="4"
        placeholder="Aliyev Vali&#10;Karimova Nodira"
      />
    </n-form-item>
    <n-button type="primary" :loading="loading" @click="submitText">Matndan qo'shish</n-button>

    <div style="margin-top: 1rem;">
      <p><a :href="sampleStudentsUrl()" target="_blank">Namuna faylni yuklab olish</a></p>
      <n-space align="center">
        <input type="file" accept=".xlsx" @change="onFileChange" />
        <n-button secondary :disabled="!file || loading" @click="submitXlsx">
          Xlsx'dan qo'shish
        </n-button>
      </n-space>
    </div>
  </div>
</template>
```

- [ ] **Step 2: `GroupsView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { listCourses, type Course } from '../../api/courses'
import { listGroups, createGroup, deleteGroup, listStudents, type Group, type Student } from '../../api/groups'
import StudentImport from '../../components/StudentImport.vue'

const message = useMessage()
const dialog = useDialog()

const courses = ref<Course[]>([])
const selectedCourseId = ref<number | null>(null)
const groups = ref<Group[]>([])
const newGroupName = ref('')

const expandedGroupId = ref<number | null>(null)
const studentsByGroup = ref<Record<number, Student[]>>({})

onMounted(async () => {
  courses.value = await listCourses()
  if (courses.value.length) {
    selectedCourseId.value = courses.value[0].id
  }
})

watch(selectedCourseId, async (id) => {
  if (id) await loadGroups(id)
})

async function loadGroups(courseId: number) {
  try {
    groups.value = await listGroups(courseId)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Guruhlarni yuklab bo'lmadi")
  }
}

async function addGroup() {
  if (!selectedCourseId.value || !newGroupName.value.trim()) return
  await createGroup({ course_id: selectedCourseId.value, name: newGroupName.value })
  newGroupName.value = ''
  message.success("Guruh qo'shildi")
  await loadGroups(selectedCourseId.value)
}

function confirmRemoveGroup(group: Group) {
  dialog.warning({
    title: "Guruhni o'chirish",
    content: `"${group.name}" guruhini o'chirishni tasdiqlaysizmi?`,
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      await deleteGroup(group.id)
      message.success("Guruh o'chirildi")
      if (selectedCourseId.value) await loadGroups(selectedCourseId.value)
    },
  })
}

async function toggleExpand(groupId: number) {
  if (expandedGroupId.value === groupId) {
    expandedGroupId.value = null
    return
  }
  expandedGroupId.value = groupId
  await loadStudents(groupId)
}

async function loadStudents(groupId: number) {
  studentsByGroup.value[groupId] = await listStudents(groupId)
}

function onStudentsImported(groupId: number) {
  loadStudents(groupId)
}
</script>

<template>
  <div>
    <h2>Guruhlar</h2>

    <n-card style="margin-bottom: 1rem;">
      <n-form-item label="Kurs">
        <n-select
          v-model:value="selectedCourseId"
          :options="courses.map((c) => ({ label: c.name, value: c.id }))"
        />
      </n-form-item>
      <n-space align="end">
        <n-form-item label="Yangi guruh nomi" style="margin-bottom: 0; flex: 1;">
          <n-input v-model:value="newGroupName" @keyup.enter="addGroup" />
        </n-form-item>
        <n-button type="primary" @click="addGroup">Qo'shish</n-button>
      </n-space>
    </n-card>

    <n-card v-for="g in groups" :key="g.id" style="margin-bottom: 1rem;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3 style="margin: 0;">{{ g.name }}</h3>
        <n-space>
          <n-button secondary @click="toggleExpand(g.id)">
            {{ expandedGroupId === g.id ? 'Yopish' : "O'quvchilar" }}
          </n-button>
          <n-button type="error" secondary @click="confirmRemoveGroup(g)">O'chirish</n-button>
        </n-space>
      </div>

      <div v-if="expandedGroupId === g.id" style="margin-top: 1rem; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 1rem;">
        <StudentImport :group-id="g.id" @imported="onStudentsImported(g.id)" />
        <n-table style="margin-top: 1rem;" single-line>
          <thead>
            <tr><th>F.I.Sh</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in studentsByGroup[g.id] || []" :key="s.id">
              <td>{{ s.full_name }}</td>
            </tr>
          </tbody>
        </n-table>
        <n-empty v-if="(studentsByGroup[g.id] || []).length === 0" description="Hozircha o'quvchilar yo'q" style="margin-top: 1rem;" />
      </div>
    </n-card>
    <n-empty v-if="groups.length === 0" description="Bu kursda guruhlar yo'q" />
  </div>
</template>
```

- [ ] **Step 3: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 4: Brauzerda qo'lda tekshirish**

`/admin/groups`ga o'ting. Tekshiring:
1. Kurs tanlash guruhlar ro'yxatini yangilaydi
2. Yangi guruh qo'shish ishlaydi
3. "O'quvchilar" tugmasi ro'yxatni ochadi/yopadi, matn/xlsx orqali qo'shish ishlaydi
4. "O'chirish" tasdiqlash dialogini ko'rsatadi

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/admin/GroupsView.vue frontend/src/components/StudentImport.vue
git commit -m "feat: GroupsView/StudentImport'ni Naive UI bilan qayta dizayn qilish"
```

---

### Task 6: ExamsView + ExamFormView

**Files:**
- Modify: `frontend/src/views/admin/ExamsView.vue`
- Modify: `frontend/src/views/admin/ExamFormView.vue`

- [ ] **Step 1: `ExamsView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NButton, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { listCourses, type Course } from '../../api/courses'
import { listExams, setExamStatus, deleteExam, type Exam } from '../../api/exams'

const message = useMessage()
const dialog = useDialog()

const courses = ref<Course[]>([])
const exams = ref<Exam[]>([])

onMounted(async () => {
  courses.value = await listCourses()
  await load()
})

async function load() {
  try {
    exams.value = await listExams()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Imtihonlarni yuklab bo'lmadi")
  }
}

function courseName(id: number) {
  return courses.value.find((c) => c.id === id)?.name || String(id)
}

async function changeStatus(exam: Exam, status: string) {
  await setExamStatus(exam.id, status)
  await load()
}

function confirmRemove(exam: Exam) {
  dialog.warning({
    title: "Imtihonni o'chirish",
    content: `"${exam.title}" imtihonini o'chirishni tasdiqlaysizmi?`,
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      await deleteExam(exam.id)
      message.success("Imtihon o'chirildi")
      await load()
    },
  })
}

function examLink(exam: Exam) {
  return `${window.location.origin}/e/${exam.access_code}`
}

function copyLink(exam: Exam) {
  navigator.clipboard.writeText(examLink(exam))
  message.success('Havola nusxalandi')
}

const columns: DataTableColumns<Exam> = [
  { title: 'Nomi', key: 'title' },
  { title: 'Kurs', key: 'course_id', render: (row) => courseName(row.course_id) },
  { title: 'Boshlanish', key: 'starts_at', render: (row) => new Date(row.starts_at).toLocaleString() },
  { title: 'Davomiylik', key: 'duration_minutes', render: (row) => `${row.duration_minutes} daq` },
  {
    title: 'Holat',
    key: 'status',
    render: (row) => h(NTag, { type: row.status === 'open' ? 'success' : 'default' }, { default: () => row.status }),
  },
  {
    title: 'Havola',
    key: 'link',
    render: (row) => h(NButton, { size: 'small', secondary: true, onClick: () => copyLink(row) }, { default: () => 'Nusxalash' }),
  },
  {
    title: '',
    key: 'actions',
    render(row) {
      const buttons = []
      if (row.status !== 'open') {
        buttons.push(h(NButton, { size: 'small', type: 'primary', onClick: () => changeStatus(row, 'open') }, { default: () => 'Ochish' }))
      }
      if (row.status === 'open') {
        buttons.push(h(NButton, { size: 'small', secondary: true, onClick: () => changeStatus(row, 'closed') }, { default: () => 'Yopish' }))
      }
      buttons.push(
        h(
          'a',
          { href: `/admin/exams/${row.id}/live-code`, style: 'text-decoration:none;' },
          h(NButton, { size: 'small', secondary: true }, { default: () => 'Kod' }),
        ),
      )
      buttons.push(
        h(
          'a',
          { href: `/admin/exams/${row.id}/results`, style: 'text-decoration:none;' },
          h(NButton, { size: 'small', secondary: true }, { default: () => 'Natijalar' }),
        ),
      )
      buttons.push(h(NButton, { size: 'small', type: 'error', secondary: true, onClick: () => confirmRemove(row) }, { default: () => "O'chirish" }))
      return h('div', { style: 'display: flex; gap: 0.4rem; flex-wrap: wrap;' }, buttons)
    },
  },
]
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
      <h2 style="margin: 0;">Imtihonlar</h2>
      <router-link to="/admin/exams/new">
        <n-button type="primary">+ Yangi imtihon</n-button>
      </router-link>
    </div>

    <n-data-table :columns="columns" :data="exams" :bordered="false" />
    <n-empty v-if="exams.length === 0" description="Hozircha imtihonlar yo'q" style="margin-top: 1rem;" />
  </div>
</template>
```

Eslatma: "Kod"/"Natijalar" havolalari uchun `<a href>` ishlatilgan, chunki `render` funksiyasi ichida `router-link` komponentini ishlatish uchun uni ham `h()` bilan alohida import qilish kerak bo'lardi — oddiy `<a href>` shu vazifa uchun yetarli va soddaroq (Vue Router `history` rejimida to'liq sahifa qayta yuklanishisiz ishlaydi, chunki bir xil origin ichida).

- [ ] **Step 2: `ExamFormView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { listCourses, type Course } from '../../api/courses'
import { listGroups, type Group } from '../../api/groups'
import { createExam } from '../../api/exams'

const router = useRouter()
const message = useMessage()
const courses = ref<Course[]>([])
const groups = ref<Group[]>([])
const loading = ref(false)

const courseId = ref<number | null>(null)
const groupId = ref<number | null>(null)
const title = ref('')
const startsAtTimestamp = ref<number | null>(null)
const durationMinutes = ref(30)
const questionCount = ref(10)
const shuffleQuestions = ref(true)
const shuffleOptions = ref(true)
const allowResume = ref(false)
const showResult = ref(true)
const totpDigits = ref(6)
const totpPeriod = ref(30)

onMounted(async () => {
  courses.value = await listCourses()
  if (courses.value.length) courseId.value = courses.value[0].id
})

watch(
  courseId,
  async (id) => {
    groups.value = id ? await listGroups(id) : []
    groupId.value = groups.value.length ? groups.value[0].id : null
  },
  { immediate: true },
)

async function submit() {
  if (!courseId.value || !groupId.value || !startsAtTimestamp.value) return
  loading.value = true
  try {
    const exam = await createExam({
      course_id: courseId.value,
      group_id: groupId.value,
      title: title.value,
      starts_at: new Date(startsAtTimestamp.value).toISOString(),
      duration_minutes: durationMinutes.value,
      question_count: questionCount.value,
      shuffle_questions: shuffleQuestions.value,
      shuffle_options: shuffleOptions.value,
      allow_resume: allowResume.value,
      show_result_to_student: showResult.value,
      totp_digits: totpDigits.value,
      totp_period: totpPeriod.value,
    })
    router.push(`/admin/exams/${exam.id}/live-code`)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Imtihon yaratib bo'lmadi")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <router-link to="/admin/exams" class="muted">&larr; Imtihonlarga qaytish</router-link>
    <h2>Yangi imtihon</h2>
    <n-card style="max-width: 500px;">
      <n-form :label-width="180">
        <n-form-item label="Kurs">
          <n-select v-model:value="courseId" :options="courses.map((c) => ({ label: c.name, value: c.id }))" />
        </n-form-item>
        <n-form-item label="Guruh">
          <n-select v-model:value="groupId" :options="groups.map((g) => ({ label: g.name, value: g.id }))" />
        </n-form-item>
        <n-form-item label="Sarlavha">
          <n-input v-model:value="title" />
        </n-form-item>
        <n-form-item label="Boshlanish sanasi va vaqti">
          <n-date-picker v-model:value="startsAtTimestamp" type="datetime" style="width: 100%;" clearable />
        </n-form-item>
        <n-form-item label="Davomiyligi (daqiqa)">
          <n-input-number v-model:value="durationMinutes" :min="1" style="width: 100%;" />
        </n-form-item>
        <n-form-item label="Savollar soni">
          <n-input-number v-model:value="questionCount" :min="1" style="width: 100%;" />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="shuffleQuestions">Savollarni aralashtirish</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="shuffleOptions">Variantlarni aralashtirish</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="allowResume">Qayta kirishga ruxsat</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="showResult">Natijani o'quvchiga ko'rsatish</n-checkbox>
        </n-form-item>
        <n-form-item label="Parol uzunligi">
          <n-select v-model:value="totpDigits" :options="[{ label: '4 xonali', value: 4 }, { label: '6 xonali', value: 6 }]" />
        </n-form-item>
        <n-form-item label="Parol almashish davri">
          <n-select v-model:value="totpPeriod" :options="[{ label: '30 soniya', value: 30 }, { label: '60 soniya', value: 60 }]" />
        </n-form-item>
        <n-button type="primary" :loading="loading" @click="submit">Yaratish</n-button>
      </n-form>
    </n-card>
  </div>
</template>
```

- [ ] **Step 3: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 4: Brauzerda qo'lda tekshirish**

`/admin/exams` va `/admin/exams/new`ga o'ting. Tekshiring:
1. Jadvalda holat `n-tag` sifatida ko'rinadi (ochiq = yashil)
2. "Nusxalash" havolani clipboard'ga nusxalaydi, toast chiqadi
3. "Ochish"/"Yopish" tugmalari holatni to'g'ri almashtiradi
4. Yangi imtihon formasi: sana-vaqt tanlagich ishlaydi, yaratilgandan keyin live-code sahifasiga o'tadi

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/admin/ExamsView.vue frontend/src/views/admin/ExamFormView.vue
git commit -m "feat: ExamsView/ExamFormView'ni Naive UI bilan qayta dizayn qilish"
```

---

### Task 7: LiveCodeView

**Files:**
- Modify: `frontend/src/views/admin/LiveCodeView.vue`

- [ ] **Step 1: To'liq faylni almashtirish**

```vue
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExam, getLiveTotp, type Exam } from '../../api/exams'

const route = useRoute()
const examId = Number(route.params.id)
const message = useMessage()

const exam = ref<Exam | null>(null)
const code = ref('')
const secondsLeft = ref(0)
let pollTimer: number | undefined

async function refresh() {
  try {
    const totp = await getLiveTotp(examId)
    code.value = totp.code
    secondsLeft.value = totp.seconds_left
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Kodni yuklab bo'lmadi")
  }
}

onMounted(async () => {
  exam.value = await getExam(examId)
  await refresh()
  pollTimer = window.setInterval(refresh, 2000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

const progressPercent = computed(() => {
  if (!exam.value) return 0
  return Math.max(0, Math.min(100, (secondsLeft.value / exam.value.totp_period) * 100))
})

const spacedCode = computed(() => code.value.split('').join(' '))
const origin = window.location.origin
</script>

<template>
  <div style="text-align: center; padding-top: 2rem;">
    <router-link to="/admin/exams" class="muted">&larr; Imtihonlarga qaytish</router-link>
    <h2 v-if="exam">{{ exam.title }}</h2>

    <n-card style="max-width: 480px; margin: 1.5rem auto; padding: 1rem;">
      <p class="muted" style="margin-bottom: 0.5rem;">Joriy parol</p>
      <div style="font-size: 4rem; font-weight: 700; letter-spacing: 0.5rem; font-family: monospace;">
        {{ spacedCode }}
      </div>
      <n-progress
        type="line"
        :percentage="progressPercent"
        :show-indicator="false"
        style="margin-top: 1.5rem;"
      />
      <p class="muted" style="margin-top: 0.5rem;">{{ secondsLeft }} soniyadan keyin yangilanadi</p>
    </n-card>

    <p v-if="exam" class="muted">
      Imtihon havolasi: <code>{{ origin }}/e/{{ exam.access_code }}</code>
    </p>
  </div>
</template>
```

- [ ] **Step 2: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 3: Brauzerda qo'lda tekshirish**

`/admin/exams/<id>/live-code`ga o'ting. Tekshiring:
1. Kod katta va aniq ko'rinadi, 2 soniyada bir yangilanadi
2. Progress-bar to'g'ri kamayadi va davr tugaganda qayta to'liq boshlanadi

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/admin/LiveCodeView.vue
git commit -m "feat: LiveCodeView'ni Naive UI bilan qayta dizayn qilish"
```

---

### Task 8: ResultsView

**Files:**
- Modify: `frontend/src/views/admin/ResultsView.vue`

- [ ] **Step 1: To'liq faylni almashtirish**

```vue
<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRoute } from 'vue-router'
import { NButton } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { getExam, getExamResults, reopenAttempt, type Exam, type AttemptResult } from '../../api/exams'

const route = useRoute()
const examId = Number(route.params.id)
const message = useMessage()
const dialog = useDialog()

const exam = ref<Exam | null>(null)
const results = ref<AttemptResult[]>([])
const loading = ref(true)
const reopeningId = ref<number | null>(null)

async function loadResults() {
  try {
    exam.value = await getExam(examId)
    results.value = await getExamResults(examId)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Natijalarni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

onMounted(loadResults)

function confirmReopen(row: AttemptResult) {
  dialog.warning({
    title: 'Qayta ochish',
    content: `${row.student_name} uchun urinishni bekor qilib, qayta topshirish imkonini berasizmi?`,
    positiveText: 'Ha',
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      reopeningId.value = row.student_id
      try {
        await reopenAttempt(examId, row.student_id)
        message.success('Qayta ochildi')
        await loadResults()
      } catch (e: any) {
        message.error(e?.response?.data?.detail || "Qayta ochib bo'lmadi")
      } finally {
        reopeningId.value = null
      }
    },
  })
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : '-'
}

const columns: DataTableColumns<AttemptResult> = [
  { title: 'F.I.Sh', key: 'student_name' },
  { title: 'Ball', key: 'score', render: (row) => `${row.score ?? '-'} / ${row.total ?? '-'}` },
  { title: 'Foiz', key: 'percent', render: (row) => (row.percent !== null ? `${row.percent}%` : '-') },
  { title: 'Baho', key: 'grade', render: (row) => row.grade ?? '-' },
  { title: 'Boshladi', key: 'started_at', render: (row) => formatDate(row.started_at) },
  { title: 'Topshirdi', key: 'submitted_at', render: (row) => formatDate(row.submitted_at) },
  { title: 'Holat', key: 'status' },
  {
    title: '',
    key: 'actions',
    render: (row) =>
      h(
        NButton,
        {
          size: 'small',
          secondary: true,
          disabled: reopeningId.value === row.student_id,
          onClick: () => confirmReopen(row),
        },
        { default: () => 'Qayta ochish' },
      ),
  },
]
</script>

<template>
  <div>
    <router-link to="/admin/exams" class="muted">&larr; Imtihonlarga qaytish</router-link>
    <h2 v-if="exam">{{ exam.title }} — Natijalar</h2>

    <n-data-table :columns="columns" :data="results" :loading="loading" :bordered="false" />
    <n-empty v-if="!loading && results.length === 0" description="Hozircha hech kim imtihon topshirmagan" style="margin-top: 1rem;" />
  </div>
</template>
```

- [ ] **Step 2: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 3: Brauzerda qo'lda tekshirish**

`/admin/exams/<id>/results`ga o'ting. Tekshiring:
1. Natijalar jadvali to'g'ri ko'rinadi, ustunlar bo'yicha saralash ishlaydi (n-data-table standart funksiyasi)
2. "Qayta ochish" tasdiqlash dialogini ko'rsatadi, tasdiqlagandan keyin qator yangilanadi

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/admin/ResultsView.vue
git commit -m "feat: ResultsView'ni n-data-table bilan qayta dizayn qilish"
```

---

### Task 9: LoginView + ProfileView

**Files:**
- Modify: `frontend/src/views/admin/LoginView.vue`
- Modify: `frontend/src/views/admin/ProfileView.vue`

- [ ] **Step 1: `LoginView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/admin')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Login yoki parol noto'g'ri")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width: 380px; margin: 0 auto; padding-top: 4rem;">
    <n-card title="Admin kirish">
      <n-form @keyup.enter="submit">
        <n-form-item label="Username">
          <n-input v-model:value="username" />
        </n-form-item>
        <n-form-item label="Parol">
          <n-input v-model:value="password" type="password" show-password-on="click" />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="submit">Kirish</n-button>
      </n-form>
    </n-card>
  </div>
</template>
```

- [ ] **Step 2: `ProfileView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../../api/client'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const message = useMessage()

const currentPassword = ref('')
const newUsername = ref('')
const newPassword = ref('')
const loading = ref(false)

onMounted(async () => {
  await auth.fetchMe()
  newUsername.value = auth.username || ''
})

async function submit() {
  loading.value = true
  try {
    const payload: Record<string, string> = { current_password: currentPassword.value }
    if (newUsername.value && newUsername.value !== auth.username) {
      payload.new_username = newUsername.value
    }
    if (newPassword.value) {
      payload.new_password = newPassword.value
    }
    const resp = await client.put('/admin/auth/me', payload)
    auth.username = resp.data.username
    message.success('Profil yangilandi')
    currentPassword.value = ''
    newPassword.value = ''
  } catch (e: any) {
    message.error(e?.response?.data?.detail || 'Xatolik yuz berdi')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2>Profil</h2>
    <n-card style="max-width: 420px;">
      <n-form>
        <n-form-item label="Joriy parol">
          <n-input v-model:value="currentPassword" type="password" show-password-on="click" />
        </n-form-item>
        <n-form-item label="Yangi username">
          <n-input v-model:value="newUsername" />
        </n-form-item>
        <n-form-item label="Yangi parol (ixtiyoriy)">
          <n-input v-model:value="newPassword" type="password" show-password-on="click" placeholder="O'zgartirmaslik uchun bo'sh qoldiring" />
        </n-form-item>
        <n-button type="primary" :loading="loading" @click="submit">Saqlash</n-button>
      </n-form>
    </n-card>
  </div>
</template>
```

- [ ] **Step 2: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 3: Brauzerda qo'lda tekshirish**

1. `/login`da noto'g'ri parol bilan xato toast'i chiqishini tekshiring, to'g'ri parol bilan `/admin`ga o'tishini tekshiring
2. `/admin/profile`da username/parolni yangilash ishlashini tekshiring

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/admin/LoginView.vue frontend/src/views/admin/ProfileView.vue
git commit -m "feat: LoginView/ProfileView'ni Naive UI bilan qayta dizayn qilish"
```

---

### Task 10: Talaba oqimi — PasswordView, PickNameView, ExamEntryView (yengil variant)

**Files:**
- Modify: `frontend/src/views/exam/PasswordView.vue`
- Modify: `frontend/src/views/exam/PickNameView.vue`
- Modify: `frontend/src/views/exam/ExamEntryView.vue`

Dizayn hujjatidagi cheklovga ko'ra, bu sahifalar faqat yengil komponentlarni (`n-button`, `n-input`, `n-card`, `n-alert`) ishlatadi — `n-data-table` kabi og'ir komponentlar yo'q.

- [ ] **Step 1: `PasswordView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { verifyCode } from '../../api/examPublic'
import { useExamStore } from '../../stores/exam'

const route = useRoute()
const router = useRouter()
const accessCode = String(route.params.accessCode)
const examStore = useExamStore()

const code = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const ok = await verifyCode(accessCode, code.value)
    if (ok) {
      examStore.code = code.value
      examStore.codeVerified = true
      router.push(`/e/${accessCode}/name`)
    }
  } catch (e: any) {
    error.value = "Parol noto'g'ri"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width: 380px; margin: 0 auto; padding-top: 3rem;">
    <n-card title="Parolni kiriting">
      <p style="color: var(--n-text-color-3, #6b7280);">O'qituvchi ekranidagi joriy kodni kiriting</p>
      <n-alert v-if="error" type="error" style="margin-bottom: 1rem;">{{ error }}</n-alert>
      <n-input
        v-model:value="code"
        size="large"
        style="text-align: center; font-size: 1.5rem; letter-spacing: 0.3rem; margin-bottom: 1rem;"
        @keyup.enter="submit"
      />
      <n-button type="primary" block size="large" :loading="loading" @click="submit">Tasdiqlash</n-button>
    </n-card>
  </div>
</template>
```

- [ ] **Step 2: `PickNameView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listAvailableStudents, startExam, type StudentPublic } from '../../api/examPublic'
import { useExamStore } from '../../stores/exam'

const route = useRoute()
const router = useRouter()
const accessCode = String(route.params.accessCode)
const examStore = useExamStore()

const students = ref<StudentPublic[]>([])
const error = ref('')
const loading = ref(true)
const starting = ref(false)

onMounted(async () => {
  if (!examStore.code) {
    router.push(`/e/${accessCode}/password`)
    return
  }
  try {
    students.value = await listAvailableStudents(accessCode, examStore.code)
  } catch (e: any) {
    error.value = "Ro'yxatni yuklab bo'lmadi"
  } finally {
    loading.value = false
  }
})

async function selectStudent(student: StudentPublic) {
  starting.value = true
  error.value = ''
  try {
    const result = await startExam(accessCode, student.id, examStore.code)
    examStore.selectedStudent = student
    examStore.attemptId = result.attempt_id
    examStore.endsAt = result.ends_at
    examStore.questions = result.questions
    examStore.persistAttempt()
    router.push(`/e/${accessCode}/test`)
  } catch (e: any) {
    if (e?.response?.status === 409) {
      error.value = 'Siz allaqachon imtihonni topshirgansiz'
    } else if (e?.response?.status === 403) {
      error.value = "Imtihon hozir ochiq emas yoki parol muddati o'tgan"
    } else {
      error.value = "Imtihonni boshlab bo'lmadi"
    }
  } finally {
    starting.value = false
  }
}
</script>

<template>
  <div style="max-width: 420px; margin: 0 auto; padding-top: 3rem;">
    <h2>Ismingizni tanlang</h2>
    <n-alert v-if="error" type="error" style="margin-bottom: 1rem;">{{ error }}</n-alert>
    <n-spin :show="loading">
      <n-space vertical style="width: 100%;">
        <n-button
          v-for="s in students"
          :key="s.id"
          secondary
          block
          style="justify-content: flex-start;"
          :disabled="starting"
          @click="selectStudent(s)"
        >
          {{ s.full_name }}
        </n-button>
      </n-space>
      <n-empty v-if="!loading && students.length === 0" description="Ro'yxatda mavjud ism qolmadi" />
    </n-spin>
  </div>
</template>
```

- [ ] **Step 3: `ExamEntryView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExamStatus, type ExamPublicStatus } from '../../api/examPublic'
import { useExamStore } from '../../stores/exam'

const route = useRoute()
const router = useRouter()
const accessCode = String(route.params.accessCode)
const examStore = useExamStore()
examStore.accessCode = accessCode

const status = ref<ExamPublicStatus | null>(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    status.value = await getExamStatus(accessCode)
  } catch (e: any) {
    error.value = e?.response?.status === 404 ? 'Imtihon topilmadi' : "Yuklab bo'lmadi"
  } finally {
    loading.value = false
  }
})

function proceed() {
  router.push(`/e/${accessCode}/password`)
}

function closedReason(s: ExamPublicStatus): string {
  if (s.status === 'draft') {
    return "Imtihon hali o'qituvchi tomonidan ochilmagan. Iltimos, o'qituvchingizga murojaat qiling."
  }
  if (s.status === 'closed') {
    return 'Imtihon yakunlangan.'
  }
  const startsAt = new Date(s.starts_at).getTime()
  const endsAt = startsAt + s.duration_minutes * 60000
  if (Date.now() < startsAt) {
    return `Imtihon hali boshlanmagan. Boshlanish vaqti: ${new Date(s.starts_at).toLocaleString()}`
  }
  if (Date.now() > endsAt) {
    return 'Imtihon vaqti tugagan.'
  }
  return 'Imtihon hozircha ochiq emas.'
}
</script>

<template>
  <div style="max-width: 420px; margin: 0 auto; padding-top: 3rem; text-align: center;">
    <n-spin v-if="loading" show />
    <n-alert v-else-if="error" type="error">{{ error }}</n-alert>
    <n-card v-else-if="status" :title="status.title">
      <p style="color: var(--n-text-color-3, #6b7280);">{{ status.group_name }}</p>
      <n-alert v-if="!status.is_open_now" type="error">{{ closedReason(status) }}</n-alert>
      <n-button v-else type="primary" block @click="proceed">Boshlash</n-button>
    </n-card>
  </div>
</template>
```

- [ ] **Step 4: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 5: Brauzerda qo'lda tekshirish**

Ochiq imtihon havolasi orqali to'liq oqimni sinab ko'ring: `/e/<code>` → parol kiritish → ism tanlash. Har bir bosqichda xatoliklar to'g'ri ko'rsatilishini tekshiring.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/exam/PasswordView.vue frontend/src/views/exam/PickNameView.vue frontend/src/views/exam/ExamEntryView.vue
git commit -m "feat: talaba-oqimi kirish sahifalarini (parol/ism/entry) Naive UI bilan qayta dizayn qilish"
```

---

### Task 11: Talaba oqimi — ExamView, ResultView (yengil variant)

**Files:**
- Modify: `frontend/src/views/exam/ExamView.vue`
- Modify: `frontend/src/views/exam/ResultView.vue`

- [ ] **Step 1: `ExamView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { submitExam } from '../../api/examPublic'
import { useExamStore } from '../../stores/exam'

const route = useRoute()
const router = useRouter()
const accessCode = String(route.params.accessCode)
const examStore = useExamStore()

const secondsLeft = ref(0)
let timer: number | undefined
const submitting = ref(false)
const error = ref('')

onMounted(() => {
  if (!examStore.attemptId || !examStore.endsAt) {
    router.push(`/e/${accessCode}`)
    return
  }
  updateSecondsLeft()
  timer = window.setInterval(() => {
    updateSecondsLeft()
    if (secondsLeft.value <= 0) {
      doSubmit()
    }
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function updateSecondsLeft() {
  if (!examStore.endsAt) return
  const end = new Date(examStore.endsAt).getTime()
  secondsLeft.value = Math.max(0, Math.round((end - Date.now()) / 1000))
}

const minutes = computed(() => Math.floor(secondsLeft.value / 60))
const seconds = computed(() => secondsLeft.value % 60)

function selectAnswer(questionId: number, index: number) {
  examStore.answers[questionId] = index
}

async function doSubmit() {
  if (submitting.value) return
  submitting.value = true
  if (timer) clearInterval(timer)
  try {
    const result = await submitExam(accessCode, examStore.attemptId as number, examStore.answers)
    examStore.clearPersistedAttempt()
    examStore.result = result
    router.push(`/e/${accessCode}/result`)
  } catch (e: any) {
    error.value = 'Topshirishda xatolik yuz berdi'
    submitting.value = false
  }
}
</script>

<template>
  <div style="max-width: 640px; margin: 0 auto; padding: 0 1rem;">
    <div
      style="position: sticky; top: 0; background: var(--n-body-color, #f8fafc); padding: 0.75rem 0; display: flex; justify-content: space-between; align-items: center; z-index: 10;"
    >
      <strong>Qolgan vaqt: {{ minutes }}:{{ seconds.toString().padStart(2, '0') }}</strong>
      <n-button type="primary" :disabled="submitting" @click="doSubmit">Topshirish</n-button>
    </div>
    <n-alert v-if="error" type="error" style="margin-bottom: 1rem;">{{ error }}</n-alert>

    <n-card v-for="(q, qi) in examStore.questions" :key="q.id" style="margin-bottom: 1rem;">
      <p><strong>{{ qi + 1 }}. {{ q.text }}</strong></p>
      <n-radio-group :value="examStore.answers[q.id]" @update:value="(v) => selectAnswer(q.id, v)">
        <n-space vertical>
          <n-radio v-for="(opt, oi) in q.options" :key="oi" :value="oi">{{ opt }}</n-radio>
        </n-space>
      </n-radio-group>
    </n-card>
  </div>
</template>
```

- [ ] **Step 2: `ResultView.vue`ni yangilash**

```vue
<script setup lang="ts">
import { useExamStore } from '../../stores/exam'

const examStore = useExamStore()
const result = examStore.result
</script>

<template>
  <div style="max-width: 420px; margin: 0 auto; padding-top: 3rem; text-align: center;">
    <n-card title="Imtihon yakunlandi">
      <template v-if="result && result.percent !== undefined">
        <p style="font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0;">{{ result.percent }}%</p>
        <p style="color: var(--n-text-color-3, #6b7280);">{{ result.score }} / {{ result.total }} to'g'ri javob</p>
        <p style="font-size: 1.5rem; font-weight: 600;">Baho: {{ result.grade }}</p>
      </template>
      <template v-else>
        <p>Javoblaringiz qabul qilindi. Natijangiz keyinroq e'lon qilinadi.</p>
      </template>
    </n-card>
  </div>
</template>
```

- [ ] **Step 3: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 4: Brauzerda qo'lda tekshirish**

To'liq imtihon oqimini sinab ko'ring: savolni tanlash, taymer to'g'ri kamayishi, "Topshirish" tugmasi ishlashi, natija sahifasi to'g'ri ko'rsatilishi. Taymer 0'ga yetganda avtomatik topshirilishini tekshiring.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/exam/ExamView.vue frontend/src/views/exam/ResultView.vue
git commit -m "feat: imtihon topshirish/natija sahifalarini Naive UI bilan qayta dizayn qilish"
```

---

### Task 12: Yakuniy tozalash

**Files:**
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Endi ishlatilmaydigan qoidalarni o'chirish**

`.btn`, `.btn-secondary`, `.btn-danger`, `.form-group`, `.alert`, `.alert-error`, `.alert-success`, `.modal-overlay`, `.modal-card`, `table`/`th`/`td` qoidalarini `style.css`dan olib tashlang — bularning barchasi endi Naive UI komponentlari bilan almashtirilgan. `.container`, `.card` (agar hali qayerda ishlatilsa), `.muted` kabi hali ishlatilayotgan sinflarni saqlab qoling.

Tekshirish uchun avval qidiruv qiling:

Run: `cd frontend && grep -rn "class=\"btn\|class=\".*btn-\|form-group\|alert-error\|alert-success\|modal-overlay" src/`

Expected: hech qanday natija chiqmasligi kerak (barcha joylarda Naive UI komponentlariga o'tilgan).

- [ ] **Step 2: Build orqali tekshirish**

Run: `cd frontend && npm run build` — xatosiz o'tishi kerak.

- [ ] **Step 3: To'liq qo'lda regressiya tekshiruvi**

Barcha admin sahifalarni (`/admin/courses`, `/admin/groups`, `/admin/exams`, `/admin/exams/new`, `/admin/exams/:id/live-code`, `/admin/exams/:id/results`, `/admin/profile`) va talaba-oqimini (`/e/:code` → `password` → `name` → `test` → `result`) qayta ko'rib chiqing — kunduzgi va tungi rejimda ikkalasida ham.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/style.css
git commit -m "chore: endi ishlatilmaydigan eski CSS qoidalarini tozalash"
```

---

## Spec qamrovi tekshiruvi

- Vizual yo'nalish (teal/shifer, 10px radius, yumshoq soya, tungi rejim) — Task 1-2 ✓
- Naive UI integratsiyasi — Task 1 ✓
- Admin sahifalar to'liq qamrovi — Task 3-9 ✓
- Talaba-oqimi yengil variant + lazy-loading orqali bundle ajratish — Task 1 (router), Task 10-11 ✓
- Sahifama-sahifa alohida commit — har bir vazifa oxirida ✓
- Backend/API o'zgarishsiz — hech bir vazifada backend fayllari o'zgartirilmagan ✓
- Eski CSS tozalash — Task 12 ✓
