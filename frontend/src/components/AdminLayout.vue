<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { darkTheme } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { useDarkMode } from '../composables/useDarkMode'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { isDark, toggle } = useDarkMode()

const menuOptions = [
  { label: 'Kurslar', key: 'admin-courses' },
  { label: 'Guruhlar', key: 'admin-groups' },
  { label: 'Imtihonlar', key: 'admin-exams' },
  { label: 'Profil', key: 'admin-profile' },
]

const activeKey = computed(() => {
  const name = String(route.name || '')
  if (name.startsWith('admin-exam')) return 'admin-exams'
  if (name === 'admin-questions') return 'admin-courses'
  return name
})

function handleMenuSelect(key: string) {
  router.push({ name: key })
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <n-layout has-sider style="min-height: 100vh;">
    <n-layout-sider
      bordered
      width="220"
      content-style="padding: 1.25rem 1rem; display: flex; flex-direction: column; min-height: 100vh; background: #0f172a;"
    >
      <n-config-provider :theme="darkTheme">
        <h3 style="margin: 0 0 1.5rem 0; color: #fff;">test-platform</h3>
        <n-menu :value="activeKey" :options="menuOptions" @update:value="handleMenuSelect" />
        <div style="margin-top: auto; display: flex; flex-direction: column; gap: 0.5rem; padding-top: 1.5rem;">
          <n-button quaternary style="justify-content: flex-start;" @click="toggle">
            {{ isDark ? '☀ Kunduzgi rejim' : '🌙 Tungi rejim' }}
          </n-button>
          <n-button secondary @click="logout">Chiqish</n-button>
        </div>
      </n-config-provider>
    </n-layout-sider>
    <n-layout-content content-style="padding: 1.5rem;">
      <div style="max-width: 1100px; margin: 0 auto;">
        <router-view />
      </div>
    </n-layout-content>
  </n-layout>
</template>
