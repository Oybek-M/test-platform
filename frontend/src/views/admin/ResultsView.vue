<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExam, getExamResults, type Exam, type AttemptResult } from '../../api/exams'

const route = useRoute()
const examId = Number(route.params.id)

const exam = ref<Exam | null>(null)
const results = ref<AttemptResult[]>([])
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    exam.value = await getExam(examId)
    results.value = await getExamResults(examId)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Natijalarni yuklab bo'lmadi"
  } finally {
    loading.value = false
  }
})

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
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && results.length === 0" class="muted">Hozircha hech kim imtihon topshirmagan.</p>
  </div>
</template>
