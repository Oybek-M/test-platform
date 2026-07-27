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
  try {
    await setExamStatus(exam.id, status)
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Holatni o'zgartirib bo'lmadi")
  }
}

function confirmRemove(exam: Exam) {
  dialog.warning({
    title: "Imtihonni o'chirish",
    content: `"${exam.title}" imtihonini o'chirishni tasdiqlaysizmi?`,
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      try {
        await deleteExam(exam.id)
        message.success("Imtihon o'chirildi")
        await load()
      } catch (e: any) {
        message.error(e?.response?.data?.detail || "O'chirib bo'lmadi")
      }
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
