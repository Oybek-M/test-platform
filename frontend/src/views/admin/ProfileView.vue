<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../../api/client'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const message = useMessage()

const currentPassword = ref('')
const newUsername = ref('')
const newPassword = ref('')
const loading = ref(false)

onMounted(async () => {
  await auth.fetchMe()
  newUsername.value = auth.username || ''
})

async function submit() {
  if (!currentPassword.value) {
    message.warning('Joriy parolni kiriting')
    return
  }
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
    message.success('Profil yangilandi')
    currentPassword.value = ''
    newPassword.value = ''
  } catch (e: any) {
    message.error(e?.response?.data?.detail || 'Xatolik yuz berdi')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2>Profil</h2>
    <n-card style="max-width: 420px;">
      <n-form>
        <n-form-item label="Joriy parol">
          <n-input v-model:value="currentPassword" type="password" show-password-on="click" />
        </n-form-item>
        <n-form-item label="Yangi username">
          <n-input v-model:value="newUsername" />
        </n-form-item>
        <n-form-item label="Yangi parol (ixtiyoriy)">
          <n-input v-model:value="newPassword" type="password" show-password-on="click" placeholder="O'zgartirmaslik uchun bo'sh qoldiring" />
        </n-form-item>
        <n-button type="primary" :loading="loading" @click="submit">Saqlash</n-button>
      </n-form>
    </n-card>
  </div>
</template>
