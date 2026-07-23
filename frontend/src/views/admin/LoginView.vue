<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/admin')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Login yoki parol noto\'g\'ri'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container" style="max-width: 380px; padding-top: 4rem;">
    <div class="card">
      <h2>Admin kirish</h2>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" required autofocus />
        </div>
        <div class="form-group">
          <label>Parol</label>
          <input v-model="password" type="password" required />
        </div>
        <button class="btn" type="submit" :disabled="loading" style="width: 100%;">
          {{ loading ? 'Kirilmoqda...' : 'Kirish' }}
        </button>
      </form>
    </div>
  </div>
</template>
