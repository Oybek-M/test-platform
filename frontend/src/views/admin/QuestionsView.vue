<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue'
import { useRoute } from 'vue-router'
import { NButton } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  listQuestions,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  type Question,
} from '../../api/questions'
import QuestionForm from '../../components/QuestionForm.vue'
import ImportDialog from '../../components/ImportDialog.vue'

const route = useRoute()
const courseId = computed(() => Number(route.params.courseId))
const message = useMessage()
const dialog = useDialog()

const questions = ref<Question[]>([])
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
    message.error(e?.response?.data?.detail || "Savollarni yuklab bo'lmadi")
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
  try {
    if (editingQuestion.value) {
      await updateQuestion(courseId.value, editingQuestion.value.id, payload)
    } else {
      await createQuestion(courseId.value, payload)
    }
    showForm.value = false
    editingQuestion.value = null
    message.success('Savol saqlandi')
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Savolni saqlab bo'lmadi")
  }
}

async function toggleActive(q: Question) {
  await updateQuestion(courseId.value, q.id, { is_active: !q.is_active })
  await load()
}

function confirmRemove(q: Question) {
  dialog.warning({
    title: "Savolni o'chirish",
    content: "Savolni o'chirishni tasdiqlaysizmi?",
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      await deleteQuestion(courseId.value, q.id)
      message.success("Savol o'chirildi")
      await load()
    },
  })
}

function onImported() {
  showImport.value = false
  load()
}

const columns: DataTableColumns<Question> = [
  { title: 'Savol', key: 'text' },
  {
    title: 'Variantlar',
    key: 'options',
    render(row) {
      return row.options
        .map((opt, i) => (i === row.correct_index ? `✓ ${opt}` : opt))
        .join(', ')
    },
  },
  { title: 'Mavzu', key: 'topic', render: (row) => row.topic || '-' },
  {
    title: 'Faol',
    key: 'is_active',
    render(row) {
      return h('input', {
        type: 'checkbox',
        checked: row.is_active,
        onChange: () => toggleActive(row),
      })
    },
  },
  {
    title: '',
    key: 'actions',
    render(row) {
      return h('div', { style: 'display: flex; gap: 0.5rem;' }, [
        h(NButton, { secondary: true, onClick: () => openEditForm(row) }, { default: () => 'Tahrirlash' }),
        h(NButton, { type: 'error', secondary: true, onClick: () => confirmRemove(row) }, { default: () => "O'chirish" }),
      ])
    },
  },
]
</script>

<template>
  <div>
    <router-link to="/admin/courses" class="muted">&larr; Kurslarga qaytish</router-link>
    <h2>Savollar</h2>

    <n-space align="end" style="margin-bottom: 1rem;">
      <n-form-item label="Mavzu bo'yicha filtr" style="margin-bottom: 0;">
        <n-input v-model:value="topicFilter" placeholder="Mavzu..." @keyup.enter="load" />
      </n-form-item>
      <n-button type="primary" @click="openCreateForm">+ Yangi savol</n-button>
      <n-button secondary @click="showImport = !showImport">Xlsx import</n-button>
    </n-space>

    <ImportDialog v-if="showImport" :course-id="courseId" @imported="onImported" @close="showImport = false" />

    <n-modal v-model:show="showForm" preset="card" :title="editingQuestion ? 'Savolni tahrirlash' : 'Yangi savol'" style="max-width: 640px;">
      <QuestionForm
        :initial="editingQuestion || undefined"
        @submit="handleSubmit"
        @cancel="showForm = false"
      />
    </n-modal>

    <n-data-table :columns="columns" :data="questions" :loading="loading" :bordered="false" />
    <n-empty v-if="!loading && questions.length === 0" description="Hozircha savollar yo'q" style="margin-top: 1rem;" />
  </div>
</template>
