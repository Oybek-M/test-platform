<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExamStatus, type ExamPublicStatus } from '../../api/examPublic'
import { useExamStore } from '../../stores/exam'

const route = useRoute()
const router = useRouter()
const accessCode = String(route.params.accessCode)
const examStore = useExamStore()
examStore.accessCode = accessCode

const status = ref<ExamPublicStatus | null>(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    status.value = await getExamStatus(accessCode)
  } catch (e: any) {
    error.value = e?.response?.status === 404 ? 'Imtihon topilmadi' : "Yuklab bo'lmadi"
  } finally {
    loading.value = false
  }
})

function proceed() {
  router.push(`/e/${accessCode}/password`)
}

function closedReason(s: ExamPublicStatus): string {
  if (s.status === 'draft') {
    return "Imtihon hali o'qituvchi tomonidan ochilmagan. Iltimos, o'qituvchingizga murojaat qiling."
  }
  if (s.status === 'closed') {
    return 'Imtihon yakunlangan.'
  }
  const startsAt = new Date(s.starts_at).getTime()
  const endsAt = startsAt + s.duration_minutes * 60000
  if (Date.now() < startsAt) {
    return `Imtihon hali boshlanmagan. Boshlanish vaqti: ${new Date(s.starts_at).toLocaleString()}`
  }
  if (Date.now() > endsAt) {
    return 'Imtihon vaqti tugagan.'
  }
  return 'Imtihon hozircha ochiq emas.'
}
</script>

<template>
  <div class="container" style="max-width: 420px; padding-top: 3rem; text-align: center;">
    <div v-if="loading">Yuklanmoqda...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="status" class="card">
      <h2>{{ status.title }}</h2>
      <p class="muted">{{ status.group_name }}</p>
      <p v-if="!status.is_open_now" class="alert alert-error">
        {{ closedReason(status) }}
      </p>
      <button v-else class="btn" @click="proceed">Boshlash</button>
    </div>
  </div>
</template>
