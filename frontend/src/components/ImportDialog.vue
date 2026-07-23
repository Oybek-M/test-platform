<script setup lang="ts">
import { ref } from 'vue'
import { importQuestions, sampleQuestionsUrl, type QuestionImportPreview } from '../api/questions'

const props = defineProps<{ courseId: number }>()
const emit = defineEmits<{ imported: []; close: [] }>()

const file = ref<File | null>(null)
const preview = ref<QuestionImportPreview | null>(null)
const errors = ref<string[]>([])
const loading = ref(false)
const errorMsg = ref('')

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  file.value = target.files?.[0] || null
  preview.value = null
  errors.value = []
  errorMsg.value = ''
}

async function doPreview() {
  if (!file.value) return
  loading.value = true
  errorMsg.value = ''
  errors.value = []
  try {
    const result = await importQuestions(props.courseId, file.value, false)
    preview.value = result as QuestionImportPreview
  } catch (e: any) {
    if (e?.response?.status === 422 && e.response.data?.detail) {
      errors.value = e.response.data.detail.errors || []
      errorMsg.value = `Faylda ${errors.value.length} ta xato topildi. Tuzatib qayta yuklang.`
    } else {
      errorMsg.value = "Faylni tahlil qilib bo'lmadi"
    }
  } finally {
    loading.value = false
  }
}

async function doConfirm() {
  if (!file.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    await importQuestions(props.courseId, file.value, true)
    emit('imported')
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail?.errors?.join(', ') || "Import qilib bo'lmadi"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card">
    <h3>Xlsx orqali savol import qilish</h3>
    <p><a :href="sampleQuestionsUrl()" target="_blank">Namuna faylni yuklab olish</a></p>
    <input type="file" accept=".xlsx" @change="onFileChange" />
    <div v-if="errorMsg" class="alert alert-error">{{ errorMsg }}</div>
    <ul v-if="errors.length" style="color: var(--color-danger);">
      <li v-for="(err, i) in errors" :key="i">{{ err }}</li>
    </ul>
    <div v-if="preview" class="alert alert-success">
      {{ preview.questions_found }} ta savol topildi. Tasdiqlab importni yakunlang.
    </div>
    <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
      <button class="btn btn-secondary" type="button" :disabled="!file || loading" @click="doPreview">
        Ko'rib chiqish
      </button>
      <button class="btn" type="button" :disabled="!preview || loading" @click="doConfirm">
        Tasdiqlash va import qilish
      </button>
      <button class="btn btn-secondary" type="button" @click="emit('close')">Yopish</button>
    </div>
  </div>
</template>
