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
  <div style="max-width: 420px; margin: 0 auto; padding-top: 3rem; text-align: center;">
    <n-spin v-if="loading" show />
    <n-alert v-else-if="error" type="error">{{ error }}</n-alert>
    <n-card v-else-if="status" :title="status.title">
      <p style="color: var(--n-text-color-3, #6b7280);">{{ status.group_name }}</p>
      <n-alert v-if="!status.is_open_now" type="error">{{ closedReason(status) }}</n-alert>
      <n-button v-else type="primary" block @click="proceed">Boshlash</n-button>
    </n-card>
  </div>
</template>
