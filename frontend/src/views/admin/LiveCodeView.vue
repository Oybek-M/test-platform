<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExam, getLiveTotp, type Exam } from '../../api/exams'

const route = useRoute()
const examId = Number(route.params.id)

const exam = ref<Exam | null>(null)
const code = ref('')
const secondsLeft = ref(0)
const error = ref('')
let pollTimer: number | undefined

async function refresh() {
  try {
    const totp = await getLiveTotp(examId)
    code.value = totp.code
    secondsLeft.value = totp.seconds_left
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Kodni yuklab bo'lmadi"
  }
}

onMounted(async () => {
  exam.value = await getExam(examId)
  await refresh()
  pollTimer = window.setInterval(refresh, 2000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

const progressPercent = computed(() => {
  if (!exam.value) return 0
  return Math.max(0, Math.min(100, (secondsLeft.value / exam.value.totp_period) * 100))
})

const spacedCode = computed(() => code.value.split('').join(' '))
const origin = window.location.origin
</script>

<template>
  <div style="text-align: center; padding-top: 2rem;">
    <router-link to="/admin/exams" class="muted">&larr; Imtihonlarga qaytish</router-link>
    <h2 v-if="exam">{{ exam.title }}</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="card" style="max-width: 480px; margin: 1.5rem auto; padding: 2.5rem;">
      <p class="muted" style="margin-bottom: 0.5rem;">Joriy parol</p>
      <div style="font-size: 4rem; font-weight: 700; letter-spacing: 0.5rem; font-family: monospace;">
        {{ spacedCode }}
      </div>
      <div style="height: 8px; background: var(--color-border); border-radius: 4px; margin-top: 1.5rem; overflow: hidden;">
        <div
          style="height: 100%; background: var(--color-primary); transition: width 1s linear;"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
      <p class="muted" style="margin-top: 0.5rem;">{{ secondsLeft }} soniyadan keyin yangilanadi</p>
    </div>

    <p v-if="exam" class="muted">
      Imtihon havolasi: <code>{{ origin }}/e/{{ exam.access_code }}</code>
    </p>
  </div>
</template>
