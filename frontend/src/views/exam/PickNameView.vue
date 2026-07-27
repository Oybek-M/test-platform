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
