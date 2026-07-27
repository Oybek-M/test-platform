<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listCourses, createCourse, updateCourse, deleteCourse, type Course, type GradeBand } from '../../api/courses'

const message = useMessage()
const dialog = useDialog()

const courses = ref<Course[]>([])
const loading = ref(false)

const newName = ref('')
const newDescription = ref('')

const editingScaleId = ref<number | null>(null)
const editingScale = ref<GradeBand[]>([])

async function load() {
  loading.value = true
  try {
    courses.value = await listCourses()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Kurslarni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function addCourse() {
  if (!newName.value.trim()) return
  try {
    await createCourse({ name: newName.value, description: newDescription.value || undefined })
    newName.value = ''
    newDescription.value = ''
    message.success("Kurs qo'shildi")
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Kurs yaratib bo'lmadi")
  }
}

function confirmRemoveCourse(course: Course) {
  dialog.warning({
    title: "Kursni o'chirish",
    content: `"${course.name}" kursini o'chirishni tasdiqlaysizmi?`,
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      await deleteCourse(course.id)
      message.success("Kurs o'chirildi")
      await load()
    },
  })
}

function startEditScale(course: Course) {
  editingScaleId.value = course.id
  editingScale.value = course.grading_scale.map((b) => ({ ...b }))
}

function addBand() {
  editingScale.value.push({ grade: '', min: 0 })
}

function removeBand(index: number) {
  editingScale.value.splice(index, 1)
}

async function saveScale(courseId: number) {
  try {
    await updateCourse(courseId, { grading_scale: editingScale.value })
    editingScaleId.value = null
    message.success('Shkala saqlandi')
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Shkalani saqlab bo'lmadi")
  }
}
</script>

<template>
  <div>
    <h2>Kurslar</h2>

    <n-card title="Yangi kurs" style="margin-bottom: 1rem;">
      <n-space align="end">
        <n-form-item label="Nomi" style="margin-bottom: 0;">
          <n-input v-model:value="newName" placeholder="Kurs nomi" />
        </n-form-item>
        <n-form-item label="Tavsif" style="margin-bottom: 0;">
          <n-input v-model:value="newDescription" placeholder="Ixtiyoriy" />
        </n-form-item>
        <n-button type="primary" @click="addCourse">Qo'shish</n-button>
      </n-space>
    </n-card>

    <n-spin :show="loading">
      <n-card v-for="course in courses" :key="course.id" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div>
            <h3 style="margin: 0;">{{ course.name }}</h3>
            <p v-if="course.description" class="muted" style="margin: 0.25rem 0 0 0;">{{ course.description }}</p>
          </div>
          <n-space>
            <router-link :to="`/admin/courses/${course.id}/questions`">
              <n-button secondary>Savollar</n-button>
            </router-link>
            <n-button secondary @click="startEditScale(course)">Baholash shkalasi</n-button>
            <n-button type="error" secondary @click="confirmRemoveCourse(course)">O'chirish</n-button>
          </n-space>
        </div>

        <div v-if="editingScaleId === course.id" style="margin-top: 1rem; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 1rem;">
          <n-space v-for="(band, i) in editingScale" :key="i" align="center" style="margin-bottom: 0.5rem;">
            <n-input v-model:value="band.grade" placeholder="Baho (A)" style="width: 100px;" />
            <n-input-number v-model:value="band.min" :min="0" :max="100" placeholder="Min %" style="width: 120px;" />
            <n-button type="error" quaternary @click="removeBand(i)">X</n-button>
          </n-space>
          <n-space>
            <n-button dashed @click="addBand">+ Daraja qo'shish</n-button>
            <n-button type="primary" @click="saveScale(course.id)">Saqlash</n-button>
            <n-button @click="editingScaleId = null">Bekor qilish</n-button>
          </n-space>
        </div>
        <p v-else class="muted" style="margin: 0.75rem 0 0 0;">
          Shkala: {{ course.grading_scale.map(b => `${b.grade}≥${b.min}`).join(' · ') }}
        </p>
      </n-card>

      <n-empty v-if="!loading && courses.length === 0" description="Hozircha kurslar yo'q" />
    </n-spin>
  </div>
</template>
