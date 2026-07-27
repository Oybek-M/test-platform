<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { listCourses, type Course } from '../../api/courses'
import { listGroups, type Group } from '../../api/groups'
import { createExam } from '../../api/exams'

const router = useRouter()
const message = useMessage()
const courses = ref<Course[]>([])
const groups = ref<Group[]>([])
const loading = ref(false)

const courseId = ref<number | null>(null)
const groupId = ref<number | null>(null)
const title = ref('')
const startsAtTimestamp = ref<number | null>(null)
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
  if (!courseId.value || !groupId.value || !startsAtTimestamp.value) return
  loading.value = true
  try {
    const exam = await createExam({
      course_id: courseId.value,
      group_id: groupId.value,
      title: title.value,
      starts_at: new Date(startsAtTimestamp.value).toISOString(),
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
    message.error(e?.response?.data?.detail || "Imtihon yaratib bo'lmadi")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <router-link to="/admin/exams" class="muted">&larr; Imtihonlarga qaytish</router-link>
    <h2>Yangi imtihon</h2>
    <n-card style="max-width: 500px;">
      <n-form :label-width="180">
        <n-form-item label="Kurs">
          <n-select v-model:value="courseId" :options="courses.map((c) => ({ label: c.name, value: c.id }))" />
        </n-form-item>
        <n-form-item label="Guruh">
          <n-select v-model:value="groupId" :options="groups.map((g) => ({ label: g.name, value: g.id }))" />
        </n-form-item>
        <n-form-item label="Sarlavha">
          <n-input v-model:value="title" />
        </n-form-item>
        <n-form-item label="Boshlanish sanasi va vaqti">
          <n-date-picker v-model:value="startsAtTimestamp" type="datetime" style="width: 100%;" clearable />
        </n-form-item>
        <n-form-item label="Davomiyligi (daqiqa)">
          <n-input-number v-model:value="durationMinutes" :min="1" style="width: 100%;" />
        </n-form-item>
        <n-form-item label="Savollar soni">
          <n-input-number v-model:value="questionCount" :min="1" style="width: 100%;" />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="shuffleQuestions">Savollarni aralashtirish</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="shuffleOptions">Variantlarni aralashtirish</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="allowResume">Qayta kirishga ruxsat</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="showResult">Natijani o'quvchiga ko'rsatish</n-checkbox>
        </n-form-item>
        <n-form-item label="Parol uzunligi">
          <n-select v-model:value="totpDigits" :options="[{ label: '4 xonali', value: 4 }, { label: '6 xonali', value: 6 }]" />
        </n-form-item>
        <n-form-item label="Parol almashish davri">
          <n-select v-model:value="totpPeriod" :options="[{ label: '30 soniya', value: 30 }, { label: '60 soniya', value: 60 }]" />
        </n-form-item>
        <n-button type="primary" :loading="loading" @click="submit">Yaratish</n-button>
      </n-form>
    </n-card>
  </div>
</template>
