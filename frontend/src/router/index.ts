import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/admin/LoginView.vue'
import ProfileView from '../views/admin/ProfileView.vue'
import CoursesView from '../views/admin/CoursesView.vue'
import QuestionsView from '../views/admin/QuestionsView.vue'
import GroupsView from '../views/admin/GroupsView.vue'
import ExamsView from '../views/admin/ExamsView.vue'
import ExamFormView from '../views/admin/ExamFormView.vue'
import LiveCodeView from '../views/admin/LiveCodeView.vue'
import AdminLayout from '../components/AdminLayout.vue'
import ExamEntryView from '../views/exam/ExamEntryView.vue'
import PasswordView from '../views/exam/PasswordView.vue'
import PickNameView from '../views/exam/PickNameView.vue'
import ExamView from '../views/exam/ExamView.vue'
import ResultView from '../views/exam/ResultView.vue'

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
        { path: 'groups', name: 'admin-groups', component: GroupsView },
        { path: 'exams', name: 'admin-exams', component: ExamsView },
        { path: 'exams/new', name: 'admin-exam-new', component: ExamFormView },
        { path: 'exams/:id/live-code', name: 'admin-exam-live-code', component: LiveCodeView },
      ],
    },
    {
      path: '/e/:accessCode',
      children: [
        { path: '', name: 'exam-entry', component: ExamEntryView },
        { path: 'password', name: 'exam-password', component: PasswordView },
        { path: 'name', name: 'exam-name', component: PickNameView },
        { path: 'test', name: 'exam-test', component: ExamView },
        { path: 'result', name: 'exam-result', component: ResultView },
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
