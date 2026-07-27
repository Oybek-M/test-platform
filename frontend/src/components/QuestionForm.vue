<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  initial?: { text: string; options: string[]; correct_index: number; topic: string | null }
}>()
const emit = defineEmits<{
  submit: [payload: { text: string; options: string[]; correct_index: number; topic?: string }]
  cancel: []
}>()
const message = useMessage()

const text = ref(props.initial?.text || '')
const options = ref<string[]>(props.initial?.options ? [...props.initial.options] : ['', ''])
const correctIndex = ref(props.initial?.correct_index ?? 0)
const topic = ref(props.initial?.topic || '')

function addOption() {
  if (options.value.length < 6) options.value.push('')
}

function removeOption(i: number) {
  if (options.value.length > 2) {
    options.value.splice(i, 1)
    if (correctIndex.value >= options.value.length) {
      correctIndex.value = options.value.length - 1
    }
  }
}

function submit() {
  const trimmedOptions = options.value.filter((o) => o.trim() !== '')
  if (!text.value.trim()) {
    message.warning('Savol matnini kiriting')
    return
  }
  if (trimmedOptions.length < 2) {
    message.warning('Kamida 2 ta variant kiriting')
    return
  }
  emit('submit', {
    text: text.value,
    options: trimmedOptions,
    correct_index: correctIndex.value,
    topic: topic.value || undefined,
  })
}
</script>

<template>
  <n-form :label-width="0">
    <n-form-item label="Savol matni">
      <n-input v-model:value="text" type="textarea" :rows="2" />
    </n-form-item>
    <n-form-item label="Variantlar (to'g'ri javobni belgilang)">
      <div style="width: 100%;">
        <n-space v-for="(_, i) in options" :key="i" align="center" style="margin-bottom: 0.5rem; width: 100%;">
          <input type="radio" name="correct-option" :checked="correctIndex === i" @change="correctIndex = i" />
          <n-input v-model:value="options[i]" :placeholder="`Variant ${i + 1}`" style="flex: 1;" />
          <n-button v-if="options.length > 2" type="error" quaternary @click="removeOption(i)">X</n-button>
        </n-space>
        <n-button v-if="options.length < 6" dashed @click="addOption">+ Variant qo'shish</n-button>
      </div>
    </n-form-item>
    <n-form-item label="Mavzu (ixtiyoriy)">
      <n-input v-model:value="topic" />
    </n-form-item>
    <n-space>
      <n-button type="primary" @click="submit">Saqlash</n-button>
      <n-button @click="emit('cancel')">Bekor qilish</n-button>
    </n-space>
  </n-form>
</template>
