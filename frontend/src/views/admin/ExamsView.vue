<script setup lang="ts">
import { onMounted, h } from 'vue'
import { NButton, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { listCourses, type Course } from '../../api/courses'
import { listExams, setExamStatus, deleteExam, type Exam } from '../../api/exams'
import { useViewCache } from '../../composables/useViewCache'

const message = useMessage()
const dialog = useDialog()

const courses = useViewCache<Course[]>('courses', [])
const exams = useViewCache<Exam[]>('exams', [])

onMounted(async () => {
  // Load courses if not cached
  if (courses.value.length === 0) {
    courses.value = await listCourses()
  }
  // Load exams if not cached
  if (exams.value.length === 0) {
    await load()
  }
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
    // Update cached exam directly without full re-fetch
    const index = exams.value.findIndex(e => e.id === exam.id)
    if (index >= 0) {
      exams.value[index] = { ...exams.value[index], status }
    }
    message.success("Holat o'zgartirildi")
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
        // Update cached exams by filtering out the deleted exam
        exams.value = exams.value.filter(e => e.id !== exam.id)
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
  {
    title: 'Nomi',
    key: 'title',
    sorter: (rowA, rowB) => rowA.title.localeCompare(rowB.title),
  },
  {
    title: 'Kurs',
    key: 'course_id',
    render: (row) => courseName(row.course_id),
    sorter: (rowA, rowB) => courseName(rowA.course_id).localeCompare(courseName(rowB.course_id)),
  },
  {
    title: 'Boshlanish',
    key: 'starts_at',
    render: (row) => new Date(row.starts_at).toLocaleString(),
    sorter: (rowA, rowB) => new Date(rowA.starts_at).getTime() - new Date(rowB.starts_at).getTime(),
  },
  {
    title: 'Davomiylik',
    key: 'duration_minutes',
    render: (row) => `${row.duration_minutes} daq`,
    sorter: (rowA, rowB) => rowA.duration_minutes - rowB.duration_minutes,
  },
  {
    title: 'Holat',
    key: 'status',
    render: (row) => h(NTag, { type: row.status === 'open' ? 'success' : 'default' }, { default: () => row.status }),
    sorter: (rowA, rowB) => rowA.status.localeCompare(rowB.status),
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
