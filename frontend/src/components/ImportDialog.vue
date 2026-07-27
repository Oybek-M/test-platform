<script setup lang="ts">
import { ref } from 'vue'
import { importQuestions, sampleQuestionsUrl, type QuestionImportPreview } from '../api/questions'

const props = defineProps<{ courseId: number }>()
const emit = defineEmits<{ imported: []; close: [] }>()
const message = useMessage()

const file = ref<File | null>(null)
const preview = ref<QuestionImportPreview | null>(null)
const errors = ref<string[]>([])
const loading = ref(false)

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  file.value = target.files?.[0] || null
  preview.value = null
  errors.value = []
}

async function doPreview() {
  if (!file.value) return
  loading.value = true
  errors.value = []
  try {
    const result = await importQuestions(props.courseId, file.value, false)
    preview.value = result as QuestionImportPreview
  } catch (e: any) {
    if (e?.response?.status === 422 && e.response.data?.detail) {
      errors.value = e.response.data.detail.errors || []
      message.error(`Faylda ${errors.value.length} ta xato topildi. Tuzatib qayta yuklang.`)
    } else {
      message.error("Faylni tahlil qilib bo'lmadi")
    }
  } finally {
    loading.value = false
  }
}

async function doConfirm() {
  if (!file.value) return
  loading.value = true
  try {
    await importQuestions(props.courseId, file.value, true)
    message.success('Savollar import qilindi')
    emit('imported')
  } catch (e: any) {
    message.error(e?.response?.data?.detail?.errors?.join(', ') || "Import qilib bo'lmadi")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <n-card title="Xlsx orqali savol import qilish" style="margin-bottom: 1rem;">
    <p><a :href="sampleQuestionsUrl()" target="_blank">Namuna faylni yuklab olish</a></p>
    <input type="file" accept=".xlsx" @change="onFileChange" />
    <n-alert v-if="errors.length" type="error" style="margin-top: 1rem;">
      <ul style="margin: 0; padding-left: 1.2rem;">
        <li v-for="(err, i) in errors" :key="i">{{ err }}</li>
      </ul>
    </n-alert>
    <n-alert v-if="preview" type="success" style="margin-top: 1rem;">
      {{ preview.questions_found }} ta savol topildi. Tasdiqlab importni yakunlang.
    </n-alert>
    <n-space style="margin-top: 1rem;">
      <n-button secondary :disabled="!file || loading" :loading="loading" @click="doPreview">
        Ko'rib chiqish
      </n-button>
      <n-button type="primary" :disabled="!preview || loading" @click="doConfirm">
        Tasdiqlash va import qilish
      </n-button>
      <n-button @click="emit('close')">Yopish</n-button>
    </n-space>
  </n-card>
</template>
