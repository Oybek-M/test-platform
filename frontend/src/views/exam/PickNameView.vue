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
      error.value = 'Imtihon hozir ochiq emas yoki parol muddati o\'tgan'
    } else {
      error.value = "Imtihonni boshlab bo'lmadi"
    }
  } finally {
    starting.value = false
  }
}
</script>

<template>
  <div class="container" style="max-width: 420px; padding-top: 3rem;">
    <h2>Ismingizni tanlang</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading">Yuklanmoqda...</div>
    <div v-else class="card">
      <button
        v-for="s in students"
        :key="s.id"
        class="btn btn-secondary"
        style="display: block; width: 100%; margin-bottom: 0.5rem; text-align: left;"
        :disabled="starting"
        @click="selectStudent(s)"
      >
        {{ s.full_name }}
      </button>
      <p v-if="students.length === 0" class="muted">Ro'yxatda mavjud ism qolmadi.</p>
    </div>
  </div>
</template>
