import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/admin/LoginView.vue'
import ProfileView from '../views/admin/ProfileView.vue'
import CoursesView from '../views/admin/CoursesView.vue'
import QuestionsView from '../views/admin/QuestionsView.vue'
import AdminLayout from '../components/AdminLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/admin' },
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/courses' },
        { path: 'profile', name: 'admin-profile', component: ProfileView },
        { path: 'courses', name: 'admin-courses', component: CoursesView },
        { path: 'courses/:courseId/questions', name: 'admin-questions', component: QuestionsView },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return { name: 'login' }
  }
  return true
})

export default router
