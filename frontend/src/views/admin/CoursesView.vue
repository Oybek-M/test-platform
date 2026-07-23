<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listCourses, createCourse, updateCourse, deleteCourse, type Course, type GradeBand } from '../../api/courses'

const courses = ref<Course[]>([])
const error = ref('')
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
    error.value = e?.response?.data?.detail || 'Kurslarni yuklab bo\'lmadi'
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function addCourse() {
  if (!newName.value.trim()) return
  error.value = ''
  try {
    await createCourse({ name: newName.value, description: newDescription.value || undefined })
    newName.value = ''
    newDescription.value = ''
    await load()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Kurs yaratib bo\'lmadi'
  }
}

async function removeCourse(id: number) {
  if (!confirm('Kursni o\'chirishni tasdiqlaysizmi?')) return
  await deleteCourse(id)
  await load()
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
  error.value = ''
  try {
    await updateCourse(courseId, { grading_scale: editingScale.value })
    editingScaleId.value = null
    await load()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Shkalani saqlab bo\'lmadi'
  }
}
</script>

<template>
  <div>
    <h2>Kurslar</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="card">
      <h3>Yangi kurs</h3>
      <form @submit.prevent="addCourse" style="display: flex; gap: 0.75rem; align-items: end; flex-wrap: wrap;">
        <div class="form-group" style="flex: 1; min-width: 200px; margin-bottom: 0;">
          <label>Nomi</label>
          <input v-model="newName" type="text" required />
        </div>
        <div class="form-group" style="flex: 2; min-width: 240px; margin-bottom: 0;">
          <label>Tavsif (ixtiyoriy)</label>
          <input v-model="newDescription" type="text" />
        </div>
        <button class="btn" type="submit">Qo'shish</button>
      </form>
    </div>

    <div class="card" v-if="loading">Yuklanmoqda...</div>

    <div v-for="course in courses" :key="course.id" class="card">
      <div style="display: flex; justify-content: space-between; align-items: start;">
        <div>
          <h3>{{ course.name }}</h3>
          <p class="muted" v-if="course.description">{{ course.description }}</p>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <router-link :to="`/admin/courses/${course.id}/questions`" class="btn btn-secondary">
            Savollar
          </router-link>
          <button class="btn btn-secondary" @click="startEditScale(course)">Baholash shkalasi</button>
          <button class="btn btn-danger" @click="removeCourse(course.id)">O'chirish</button>
        </div>
      </div>

      <div v-if="editingScaleId === course.id" style="margin-top: 1rem; border-top: 1px solid var(--color-border); padding-top: 1rem;">
        <div v-for="(band, i) in editingScale" :key="i" style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem; align-items: center;">
          <input v-model="band.grade" placeholder="Baho (A)" style="width: 100px;" />
          <input v-model.number="band.min" type="number" min="0" max="100" placeholder="Min %" style="width: 100px;" />
          <button class="btn btn-danger" type="button" @click="removeBand(i)">X</button>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-secondary" type="button" @click="addBand">+ Daraja qo'shish</button>
          <button class="btn" type="button" @click="saveScale(course.id)">Saqlash</button>
          <button class="btn btn-secondary" type="button" @click="editingScaleId = null">Bekor qilish</button>
        </div>
      </div>
      <div v-else class="muted">
        Shkala: {{ course.grading_scale.map(b => `${b.grade}≥${b.min}`).join(' · ') }}
      </div>
    </div>

    <p v-if="!loading && courses.length === 0" class="muted">Hozircha kurslar yo'q.</p>
  </div>
</template>
