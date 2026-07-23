<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { listCourses, type Course } from '../../api/courses'
import { listGroups, type Group } from '../../api/groups'
import { createExam } from '../../api/exams'

const router = useRouter()
const courses = ref<Course[]>([])
const groups = ref<Group[]>([])
const error = ref('')
const loading = ref(false)

const courseId = ref<number | null>(null)
const groupId = ref<number | null>(null)
const title = ref('')
const startsAt = ref('')
const durationMinutes = ref(30)
const questionCount = ref(10)
const shuffleQuestions = ref(true)
const shuffleOptions = ref(true)
const allowResume = ref(false)
const showResult = ref(true)
const totpDigits = ref(6)
const totpPeriod = ref(30)

onMounted(async () => {
  courses.value = await listCourses()
  if (courses.value.length) courseId.value = courses.value[0].id
})

watch(
  courseId,
  async (id) => {
    groups.value = id ? await listGroups(id) : []
    groupId.value = groups.value.length ? groups.value[0].id : null
  },
  { immediate: true },
)

async function submit() {
  if (!courseId.value || !groupId.value) return
  error.value = ''
  loading.value = true
  try {
    const exam = await createExam({
      course_id: courseId.value,
      group_id: groupId.value,
      title: title.value,
      starts_at: new Date(startsAt.value).toISOString(),
      duration_minutes: durationMinutes.value,
      question_count: questionCount.value,
      shuffle_questions: shuffleQuestions.value,
      shuffle_options: shuffleOptions.value,
      allow_resume: allowResume.value,
      show_result_to_student: showResult.value,
      totp_digits: totpDigits.value,
      totp_period: totpPeriod.value,
    })
    router.push(`/admin/exams/${exam.id}/live-code`)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Imtihon yaratib bo'lmadi"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <router-link to="/admin/exams" class="muted">&larr; Imtihonlarga qaytish</router-link>
    <h2>Yangi imtihon</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <form @submit.prevent="submit" class="card" style="max-width: 500px;">
      <div class="form-group">
        <label>Kurs</label>
        <select v-model.number="courseId">
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>Guruh</label>
        <select v-model.number="groupId">
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>Sarlavha</label>
        <input v-model="title" type="text" required />
      </div>
      <div class="form-group">
        <label>Boshlanish sanasi va vaqti</label>
        <input v-model="startsAt" type="datetime-local" required />
      </div>
      <div class="form-group">
        <label>Davomiyligi (daqiqa)</label>
        <input v-model.number="durationMinutes" type="number" min="1" required />
      </div>
      <div class="form-group">
        <label>Savollar soni</label>
        <input v-model.number="questionCount" type="number" min="1" required />
      </div>
      <div class="form-group">
        <label><input type="checkbox" v-model="shuffleQuestions" /> Savollarni aralashtirish</label>
      </div>
      <div class="form-group">
        <label><input type="checkbox" v-model="shuffleOptions" /> Variantlarni aralashtirish</label>
      </div>
      <div class="form-group">
        <label><input type="checkbox" v-model="allowResume" /> Qayta kirishga ruxsat</label>
      </div>
      <div class="form-group">
        <label><input type="checkbox" v-model="showResult" /> Natijani o'quvchiga ko'rsatish</label>
      </div>
      <div class="form-group">
        <label>Parol uzunligi</label>
        <select v-model.number="totpDigits">
          <option :value="4">4 xonali</option>
          <option :value="6">6 xonali</option>
        </select>
      </div>
      <div class="form-group">
        <label>Parol almashish davri</label>
        <select v-model.number="totpPeriod">
          <option :value="30">30 soniya</option>
          <option :value="60">60 soniya</option>
        </select>
      </div>
      <button class="btn" type="submit" :disabled="loading">
        {{ loading ? 'Yaratilmoqda...' : 'Yaratish' }}
      </button>
    </form>
  </div>
</template>
