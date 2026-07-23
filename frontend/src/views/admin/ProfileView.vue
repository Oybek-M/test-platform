<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../../api/client'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()

const currentPassword = ref('')
const newUsername = ref('')
const newPassword = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

onMounted(async () => {
  await auth.fetchMe()
  newUsername.value = auth.username || ''
})

async function submit() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const payload: Record<string, string> = { current_password: currentPassword.value }
    if (newUsername.value && newUsername.value !== auth.username) {
      payload.new_username = newUsername.value
    }
    if (newPassword.value) {
      payload.new_password = newPassword.value
    }
    const resp = await client.put('/admin/auth/me', payload)
    auth.username = resp.data.username
    success.value = 'Profil yangilandi'
    currentPassword.value = ''
    newPassword.value = ''
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Xatolik yuz berdi'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2>Profil</h2>
    <div class="card" style="max-width: 420px;">
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Joriy parol</label>
          <input v-model="currentPassword" type="password" required />
        </div>
        <div class="form-group">
          <label>Yangi username</label>
          <input v-model="newUsername" type="text" />
        </div>
        <div class="form-group">
          <label>Yangi parol (ixtiyoriy)</label>
          <input v-model="newPassword" type="password" placeholder="O'zgartirmaslik uchun bo'sh qoldiring" />
        </div>
        <button class="btn" type="submit" :disabled="loading">
          {{ loading ? 'Saqlanmoqda...' : 'Saqlash' }}
        </button>
      </form>
    </div>
  </div>
</template>
