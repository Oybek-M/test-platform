<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExam, getLiveTotp, type Exam } from '../../api/exams'

const route = useRoute()
const examId = Number(route.params.id)
const message = useMessage()

const exam = ref<Exam | null>(null)
const code = ref('')
const secondsLeft = ref(0)
let pollTimer: number | undefined

async function refresh() {
  try {
    const totp = await getLiveTotp(examId)
    code.value = totp.code
    secondsLeft.value = totp.seconds_left
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Kodni yuklab bo'lmadi")
  }
}

onMounted(async () => {
  try {
    exam.value = await getExam(examId)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Imtihon ma'lumotlarini yuklab bo'lmadi")
    return
  }
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

    <n-card style="max-width: 480px; margin: 1.5rem auto; padding: 1rem;">
      <p class="muted" style="margin-bottom: 0.5rem;">Joriy parol</p>
      <div style="font-size: 4rem; font-weight: 700; letter-spacing: 0.5rem; font-family: monospace;">
        {{ spacedCode }}
      </div>
      <n-progress
        type="line"
        :percentage="progressPercent"
        :show-indicator="false"
        style="margin-top: 1.5rem;"
      />
      <p class="muted" style="margin-top: 0.5rem;">{{ secondsLeft }} soniyadan keyin yangilanadi</p>
    </n-card>

    <p v-if="exam" class="muted">
      Imtihon havolasi: <code>{{ origin }}/e/{{ exam.access_code }}</code>
    </p>
  </div>
</template>
