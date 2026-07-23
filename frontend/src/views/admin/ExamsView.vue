<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listCourses, type Course } from '../../api/courses'
import { listExams, setExamStatus, deleteExam, type Exam } from '../../api/exams'

const courses = ref<Course[]>([])
const exams = ref<Exam[]>([])
const error = ref('')

onMounted(async () => {
  courses.value = await listCourses()
  await load()
})

async function load() {
  try {
    exams.value = await listExams()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Imtihonlarni yuklab bo'lmadi"
  }
}

function courseName(id: number) {
  return courses.value.find((c) => c.id === id)?.name || String(id)
}

async function changeStatus(exam: Exam, status: string) {
  await setExamStatus(exam.id, status)
  await load()
}

async function removeExam(id: number) {
  if (!confirm("Imtihonni o'chirishni tasdiqlaysizmi?")) return
  await deleteExam(id)
  await load()
}

function examLink(exam: Exam) {
  return `${window.location.origin}/e/${exam.access_code}`
}

function copyLink(exam: Exam) {
  navigator.clipboard.writeText(examLink(exam))
}
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h2>Imtihonlar</h2>
      <router-link to="/admin/exams/new" class="btn">+ Yangi imtihon</router-link>
    </div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <table>
      <thead>
        <tr>
          <th>Nomi</th>
          <th>Kurs</th>
          <th>Boshlanish</th>
          <th>Davomiylik</th>
          <th>Holat</th>
          <th>Havola</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ex in exams" :key="ex.id">
          <td>{{ ex.title }}</td>
          <td>{{ courseName(ex.course_id) }}</td>
          <td>{{ new Date(ex.starts_at).toLocaleString() }}</td>
          <td>{{ ex.duration_minutes }} daq</td>
          <td>{{ ex.status }}</td>
          <td>
            <button class="btn btn-secondary" @click="copyLink(ex)">Nusxalash</button>
          </td>
          <td style="white-space: nowrap;">
            <button v-if="ex.status !== 'open'" class="btn" @click="changeStatus(ex, 'open')">Ochish</button>
            <button v-if="ex.status === 'open'" class="btn btn-secondary" @click="changeStatus(ex, 'closed')">
              Yopish
            </button>
            <router-link :to="`/admin/exams/${ex.id}/live-code`" class="btn btn-secondary">Kod</router-link>
            <router-link :to="`/admin/exams/${ex.id}/results`" class="btn btn-secondary">Natijalar</router-link>
            <button class="btn btn-danger" @click="removeExam(ex.id)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="exams.length === 0" class="muted">Hozircha imtihonlar yo'q.</p>
  </div>
</template>
