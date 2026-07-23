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
  <div class="container" style="max-width: 640px;">
    <div
      style="position: sticky; top: 0; background: var(--color-bg); padding: 0.75rem 0; display: flex; justify-content: space-between; align-items: center;"
    >
      <strong>Qolgan vaqt: {{ minutes }}:{{ seconds.toString().padStart(2, '0') }}</strong>
      <button class="btn" :disabled="submitting" @click="doSubmit">Topshirish</button>
    </div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-for="(q, qi) in examStore.questions" :key="q.id" class="card">
      <p><strong>{{ qi + 1 }}. {{ q.text }}</strong></p>
      <div v-for="(opt, oi) in q.options" :key="oi" style="margin-bottom: 0.4rem;">
        <label style="display: flex; gap: 0.5rem; align-items: center; cursor: pointer;">
          <input
            type="radio"
            :name="`q-${q.id}`"
            :checked="examStore.answers[q.id] === oi"
            @change="selectAnswer(q.id, oi)"
          />
          {{ opt }}
        </label>
      </div>
    </div>
  </div>
</template>
