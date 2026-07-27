<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExam, getExamResults, reopenAttempt, type Exam, type AttemptResult } from '../../api/exams'

const route = useRoute()
const examId = Number(route.params.id)

const exam = ref<Exam | null>(null)
const results = ref<AttemptResult[]>([])
const error = ref('')
const loading = ref(true)
const reopeningId = ref<number | null>(null)

async function loadResults() {
  try {
    exam.value = await getExam(examId)
    results.value = await getExamResults(examId)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Natijalarni yuklab bo'lmadi"
  } finally {
    loading.value = false
  }
}

onMounted(loadResults)

async function handleReopen(studentId: number, studentName: string) {
  if (!confirm(`${studentName} uchun urinishni bekor qilib, qayta topshirish imkonini berasizmi?`)) {
    return
  }
  reopeningId.value = studentId
  try {
    await reopenAttempt(examId, studentId)
    await loadResults()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Qayta ochib bo'lmadi"
  } finally {
    reopeningId.value = null
  }
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : '-'
}
</script>

<template>
  <div>
    <router-link to="/admin/exams" class="muted">&larr; Imtihonlarga qaytish</router-link>
    <h2 v-if="exam">{{ exam.title }} — Natijalar</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading">Yuklanmoqda...</div>

    <table v-else>
      <thead>
        <tr>
          <th>F.I.Sh</th>
          <th>Ball</th>
          <th>Foiz</th>
          <th>Baho</th>
          <th>Boshladi</th>
          <th>Topshirdi</th>
          <th>Holat</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in results" :key="r.student_id">
          <td>{{ r.student_name }}</td>
          <td>{{ r.score ?? '-' }} / {{ r.total ?? '-' }}</td>
          <td>{{ r.percent !== null ? r.percent + '%' : '-' }}</td>
          <td>{{ r.grade ?? '-' }}</td>
          <td>{{ formatDate(r.started_at) }}</td>
          <td>{{ formatDate(r.submitted_at) }}</td>
          <td>{{ r.status }}</td>
          <td>
            <button
              class="btn btn-secondary"
              :disabled="reopeningId === r.student_id"
              @click="handleReopen(r.student_id, r.student_name)"
            >
              Qayta ochish
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && results.length === 0" class="muted">Hozircha hech kim imtihon topshirmagan.</p>
  </div>
</template>
