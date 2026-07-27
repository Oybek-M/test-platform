<script setup lang="ts">
import { ref } from 'vue'
import { addStudentsFromText, addStudentsFromXlsx, sampleStudentsUrl } from '../api/groups'

const props = defineProps<{ groupId: number }>()
const emit = defineEmits<{ imported: [] }>()
const message = useMessage()

const textInput = ref('')
const file = ref<File | null>(null)
const loading = ref(false)

function onFileChange(e: Event) {
  file.value = (e.target as HTMLInputElement).files?.[0] || null
}

async function submitText() {
  if (!textInput.value.trim()) return
  loading.value = true
  try {
    const result = await addStudentsFromText(props.groupId, textInput.value)
    if (result.warnings.length) {
      message.warning(result.warnings.join('; '))
    } else {
      message.success("O'quvchilar qo'shildi")
    }
    textInput.value = ''
    emit('imported')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "O'quvchilarni qo'shib bo'lmadi")
  } finally {
    loading.value = false
  }
}

async function submitXlsx() {
  if (!file.value) return
  loading.value = true
  try {
    const result = await addStudentsFromXlsx(props.groupId, file.value)
    if (result.warnings.length) {
      message.warning(result.warnings.join('; '))
    } else {
      message.success("O'quvchilar qo'shildi")
    }
    file.value = null
    emit('imported')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Faylni import qilib bo'lmadi")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h4>O'quvchi qo'shish</h4>
    <n-form-item label="Har qatorga bitta F.I.Sh">
      <n-input
        v-model:value="textInput"
        type="textarea"
        :rows="4"
        placeholder="Aliyev Vali&#10;Karimova Nodira"
      />
    </n-form-item>
    <n-button type="primary" :loading="loading" @click="submitText">Matndan qo'shish</n-button>

    <div style="margin-top: 1rem;">
      <p><a :href="sampleStudentsUrl()" target="_blank">Namuna faylni yuklab olish</a></p>
      <n-space align="center">
        <input type="file" accept=".xlsx" @change="onFileChange" />
        <n-button secondary :disabled="!file || loading" @click="submitXlsx">
          Xlsx'dan qo'shish
        </n-button>
      </n-space>
    </div>
  </div>
</template>
