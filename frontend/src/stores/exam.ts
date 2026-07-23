import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PublicQuestion, StudentPublic, SubmitResult } from '../api/examPublic'

export const useExamStore = defineStore('exam', () => {
  const accessCode = ref('')
  const code = ref('')
  const codeVerified = ref(false)
  const students = ref<StudentPublic[]>([])
  const selectedStudent = ref<StudentPublic | null>(null)
  const attemptId = ref<number | null>(null)
  const endsAt = ref<string | null>(null)
  const questions = ref<PublicQuestion[]>([])
  const answers = ref<Record<number, number>>({})
  const result = ref<SubmitResult | null>(null)

  function persistAttempt() {
    if (attemptId.value) {
      localStorage.setItem(`exam_attempt_${accessCode.value}`, String(attemptId.value))
    }
  }

  function clearPersistedAttempt() {
    localStorage.removeItem(`exam_attempt_${accessCode.value}`)
  }

  return {
    accessCode,
    code,
    codeVerified,
    students,
    selectedStudent,
    attemptId,
    endsAt,
    questions,
    answers,
    result,
    persistAttempt,
    clearPersistedAttempt,
  }
})
