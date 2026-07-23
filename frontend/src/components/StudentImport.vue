<script setup lang="ts">
import { ref } from 'vue'
import { addStudentsFromText, addStudentsFromXlsx, sampleStudentsUrl } from '../api/groups'

const props = defineProps<{ groupId: number }>()
const emit = defineEmits<{ imported: [] }>()

const textInput = ref('')
const file = ref<File | null>(null)
const warnings = ref<string[]>([])
const error = ref('')
const loading = ref(false)

function onFileChange(e: Event) {
  file.value = (e.target as HTMLInputElement).files?.[0] || null
}

async function submitText() {
  if (!textInput.value.trim()) return
  loading.value = true
  error.value = ''
  warnings.value = []
  try {
    const result = await addStudentsFromText(props.groupId, textInput.value)
    warnings.value = result.warnings
    textInput.value = ''
    emit('imported')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "O'quvchilarni qo'shib bo'lmadi"
  } finally {
    loading.value = false
  }
}

async function submitXlsx() {
  if (!file.value) return
  loading.value = true
  error.value = ''
  warnings.value = []
  try {
    const result = await addStudentsFromXlsx(props.groupId, file.value)
    warnings.value = result.warnings
    file.value = null
    emit('imported')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Faylni import qilib bo'lmadi"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h4>O'quvchi qo'shish</h4>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="warnings.length" class="alert alert-error">
      <div v-for="(w, i) in warnings" :key="i">{{ w }}</div>
    </div>
    <div class="form-group">
      <label>Har qatorga bitta F.I.Sh</label>
      <textarea v-model="textInput" rows="4" placeholder="Aliyev Vali&#10;Karimova Nodira"></textarea>
    </div>
    <button class="btn" type="button" :disabled="loading" @click="submitText">Matndan qo'shish</button>

    <div style="margin-top: 1rem;">
      <p><a :href="sampleStudentsUrl()" target="_blank">Namuna faylni yuklab olish</a></p>
      <input type="file" accept=".xlsx" @change="onFileChange" />
      <button class="btn btn-secondary" type="button" :disabled="!file || loading" @click="submitXlsx">
        Xlsx'dan qo'shish
      </button>
    </div>
  </div>
</template>
