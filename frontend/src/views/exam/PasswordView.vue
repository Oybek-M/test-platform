<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { verifyCode } from '../../api/examPublic'
import { useExamStore } from '../../stores/exam'

const route = useRoute()
const router = useRouter()
const accessCode = String(route.params.accessCode)
const examStore = useExamStore()

const code = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const ok = await verifyCode(accessCode, code.value)
    if (ok) {
      examStore.code = code.value
      examStore.codeVerified = true
      router.push(`/e/${accessCode}/name`)
    }
  } catch (e: any) {
    error.value = "Parol noto'g'ri"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width: 380px; margin: 0 auto; padding-top: 3rem;">
    <n-card title="Parolni kiriting">
      <p style="color: var(--n-text-color-3, #6b7280);">O'qituvchi ekranidagi joriy kodni kiriting</p>
      <n-alert v-if="error" type="error" style="margin-bottom: 1rem;">{{ error }}</n-alert>
      <n-input
        v-model:value="code"
        size="large"
        inputmode="numeric"
        autofocus
        style="text-align: center; font-size: 1.5rem; letter-spacing: 0.3rem; margin-bottom: 1rem;"
        @keyup.enter="submit"
      />
      <n-button type="primary" block size="large" :loading="loading" @click="submit">Tasdiqlash</n-button>
    </n-card>
  </div>
</template>
