<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  listQuestions,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  type Question,
} from '../../api/questions'
import QuestionForm from '../../components/QuestionForm.vue'
import ImportDialog from '../../components/ImportDialog.vue'
import Modal from '../../components/Modal.vue'

const route = useRoute()
const courseId = computed(() => Number(route.params.courseId))

const questions = ref<Question[]>([])
const error = ref('')
const loading = ref(false)

const topicFilter = ref('')
const showForm = ref(false)
const showImport = ref(false)
const editingQuestion = ref<Question | null>(null)

async function load() {
  loading.value = true
  try {
    questions.value = await listQuestions(courseId.value, {
      topic: topicFilter.value || undefined,
    })
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Savollarni yuklab bo'lmadi"
  } finally {
    loading.value = false
  }
}

onMounted(load)

function openCreateForm() {
  editingQuestion.value = null
  showForm.value = true
}

function openEditForm(q: Question) {
  editingQuestion.value = q
  showForm.value = true
}

async function handleSubmit(payload: { text: string; options: string[]; correct_index: number; topic?: string }) {
  error.value = ''
  try {
    if (editingQuestion.value) {
      await updateQuestion(courseId.value, editingQuestion.value.id, payload)
    } else {
      await createQuestion(courseId.value, payload)
    }
    showForm.value = false
    editingQuestion.value = null
    await load()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Savolni saqlab bo'lmadi"
  }
}

async function toggleActive(q: Question) {
  await updateQuestion(courseId.value, q.id, { is_active: !q.is_active })
  await load()
}

async function removeQuestion(id: number) {
  if (!confirm("Savolni o'chirishni tasdiqlaysizmi?")) return
  await deleteQuestion(courseId.value, id)
  await load()
}

function onImported() {
  showImport.value = false
  load()
}
</script>

<template>
  <div>
    <router-link to="/admin/courses" class="muted">&larr; Kurslarga qaytish</router-link>
    <h2>Savollar</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem; align-items: end; flex-wrap: wrap;">
      <div class="form-group" style="margin-bottom: 0;">
        <label>Mavzu bo'yicha filtr</label>
        <input v-model="topicFilter" type="text" @change="load" placeholder="Mavzu..." />
      </div>
      <button class="btn" @click="openCreateForm">+ Yangi savol</button>
      <button class="btn btn-secondary" @click="showImport = !showImport">Xlsx import</button>
    </div>

    <ImportDialog v-if="showImport" :course-id="courseId" @imported="onImported" @close="showImport = false" />

    <Modal v-if="showForm" @close="showForm = false">
      <h3>{{ editingQuestion ? 'Savolni tahrirlash' : 'Yangi savol' }}</h3>
      <QuestionForm
        :initial="editingQuestion || undefined"
        @submit="handleSubmit"
        @cancel="showForm = false"
      />
    </Modal>

    <div class="card" v-if="loading">Yuklanmoqda...</div>

    <table v-if="!loading">
      <thead>
        <tr>
          <th>Savol</th>
          <th>Variantlar</th>
          <th>Mavzu</th>
          <th>Faol</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in questions" :key="q.id">
          <td>{{ q.text }}</td>
          <td>
            <span v-for="(opt, i) in q.options" :key="i" :style="i === q.correct_index ? 'font-weight:600;color:var(--color-success);' : ''">
              {{ opt }}{{ i < q.options.length - 1 ? ', ' : '' }}
            </span>
          </td>
          <td>{{ q.topic || '-' }}</td>
          <td>
            <input type="checkbox" :checked="q.is_active" @change="toggleActive(q)" />
          </td>
          <td style="white-space: nowrap;">
            <button class="btn btn-secondary" @click="openEditForm(q)">Tahrirlash</button>
            <button class="btn btn-danger" @click="removeQuestion(q.id)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && questions.length === 0" class="muted">Hozircha savollar yo'q.</p>
  </div>
</template>
