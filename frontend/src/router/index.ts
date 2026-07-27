import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const LoginView = () => import('../views/admin/LoginView.vue')
const ProfileView = () => import('../views/admin/ProfileView.vue')
const CoursesView = () => import('../views/admin/CoursesView.vue')
const QuestionsView = () => import('../views/admin/QuestionsView.vue')
const GroupsView = () => import('../views/admin/GroupsView.vue')
const ExamsView = () => import('../views/admin/ExamsView.vue')
const ExamFormView = () => import('../views/admin/ExamFormView.vue')
const LiveCodeView = () => import('../views/admin/LiveCodeView.vue')
const ResultsView = () => import('../views/admin/ResultsView.vue')
const AdminLayout = () => import('../components/AdminLayout.vue')
const ExamEntryView = () => import('../views/exam/ExamEntryView.vue')
const PasswordView = () => import('../views/exam/PasswordView.vue')
const PickNameView = () => import('../views/exam/PickNameView.vue')
const ExamView = () => import('../views/exam/ExamView.vue')
const ResultView = () => import('../views/exam/ResultView.vue')

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
        { path: 'exams/:id/results', name: 'admin-exam-results', component: ResultsView },
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
