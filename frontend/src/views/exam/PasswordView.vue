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
  <div class="container" style="max-width: 380px; padding-top: 3rem;">
    <div class="card">
      <h2>Parolni kiriting</h2>
      <p class="muted">O'qituvchi ekranidagi joriy kodni kiriting</p>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="form-group">
          <input
            v-model="code"
            type="text"
            inputmode="numeric"
            required
            autofocus
            style="font-size: 1.5rem; text-align: center; letter-spacing: 0.3rem;"
          />
        </div>
        <button class="btn" type="submit" :disabled="loading" style="width: 100%;">Tasdiqlash</button>
      </form>
    </div>
  </div>
</template>
