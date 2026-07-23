<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div style="display: flex; min-height: 100vh;">
    <aside style="width: 220px; background: #1f2430; color: #fff; padding: 1.25rem 1rem; flex-shrink: 0;">
      <h3 style="color: #fff; margin-bottom: 1.5rem;">test-platform</h3>
      <nav style="display: flex; flex-direction: column; gap: 0.4rem;">
        <router-link to="/admin/courses" class="nav-link">Kurslar</router-link>
        <router-link to="/admin/groups" class="nav-link">Guruhlar</router-link>
        <router-link to="/admin/exams" class="nav-link">Imtihonlar</router-link>
        <router-link to="/admin/profile" class="nav-link">Profil</router-link>
      </nav>
      <button class="btn btn-secondary" style="margin-top: 2rem; width: 100%;" @click="logout">
        Chiqish
      </button>
    </aside>
    <main style="flex: 1; overflow-x: auto;">
      <div class="container">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.nav-link {
  color: #cdd3e0;
  text-decoration: none;
  padding: 0.5rem 0.6rem;
  border-radius: 6px;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
</style>
