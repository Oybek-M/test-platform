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
      <n-radio-group :value="examStore.answers[q.id]" @update:value="(v: number) => selectAnswer(q.id, v)">
        <n-space vertical>
          <n-radio v-for="(opt, oi) in q.options" :key="oi" :value="oi">{{ opt }}</n-radio>
        </n-space>
      </n-radio-group>
    </n-card>
  </div>
</template>
