import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const TOKEN_KEY = 'test_platform_admin_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const username = ref<string | null>(null)

  async function login(usernameInput: string, password: string) {
    const resp = await axios.post('/api/admin/auth/login', {
      username: usernameInput,
      password,
    })
    token.value = resp.data.access_token
    localStorage.setItem(TOKEN_KEY, resp.data.access_token)
    await fetchMe()
  }

  async function fetchMe() {
    if (!token.value) return
    const resp = await axios.get('/api/admin/auth/me', {
      headers: { Authorization: `Bearer ${token.value}` },
    })
    username.value = resp.data.username
  }

  function logout() {
    token.value = null
    username.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, username, login, fetchMe, logout }
})
