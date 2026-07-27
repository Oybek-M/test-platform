<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value.trim() || !password.value) {
    message.warning('Username va parolni kiriting')
    return
  }
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/admin')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Login yoki parol noto'g'ri")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width: 380px; margin: 0 auto; padding-top: 4rem;">
    <n-card title="Admin kirish">
      <n-form @keyup.enter="submit">
        <n-form-item label="Username">
          <n-input v-model:value="username" />
        </n-form-item>
        <n-form-item label="Parol">
          <n-input v-model:value="password" type="password" show-password-on="click" />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="submit">Kirish</n-button>
      </n-form>
    </n-card>
  </div>
</template>
