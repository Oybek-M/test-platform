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
  {
    title: 'F.I.Sh',
    key: 'student_name',
    sorter: (rowA, rowB) => rowA.student_name.localeCompare(rowB.student_name),
  },
  {
    title: 'Ball',
    key: 'score',
    render: (row) => `${row.score ?? '-'} / ${row.total ?? '-'}`,
    sorter: (rowA, rowB) => (rowA.score ?? -1) - (rowB.score ?? -1),
  },
  {
    title: 'Foiz',
    key: 'percent',
    render: (row) => (row.percent !== null ? `${row.percent}%` : '-'),
    sorter: (rowA, rowB) => (rowA.percent ?? -1) - (rowB.percent ?? -1),
  },
  {
    title: 'Baho',
    key: 'grade',
    render: (row) => row.grade ?? '-',
    sorter: (rowA, rowB) => (rowA.grade || '').localeCompare(rowB.grade || ''),
  },
  {
    title: 'Boshladi',
    key: 'started_at',
    render: (row) => formatDate(row.started_at),
    sorter: (rowA, rowB) => {
      const timeA = rowA.started_at ? new Date(rowA.started_at).getTime() : -1
      const timeB = rowB.started_at ? new Date(rowB.started_at).getTime() : -1
      return timeA - timeB
    },
  },
  {
    title: 'Topshirdi',
    key: 'submitted_at',
    render: (row) => formatDate(row.submitted_at),
    sorter: (rowA, rowB) => {
      const timeA = rowA.submitted_at ? new Date(rowA.submitted_at).getTime() : -1
      const timeB = rowB.submitted_at ? new Date(rowB.submitted_at).getTime() : -1
      return timeA - timeB
    },
  },
  {
    title: 'Holat',
    key: 'status',
    sorter: (rowA, rowB) => rowA.status.localeCompare(rowB.status),
  },
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
