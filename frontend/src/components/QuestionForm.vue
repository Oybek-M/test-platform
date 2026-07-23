<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  initial?: { text: string; options: string[]; correct_index: number; topic: string | null }
}>()
const emit = defineEmits<{
  submit: [payload: { text: string; options: string[]; correct_index: number; topic?: string }]
  cancel: []
}>()

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
  emit('submit', {
    text: text.value,
    options: options.value.filter((o) => o.trim() !== ''),
    correct_index: correctIndex.value,
    topic: topic.value || undefined,
  })
}
</script>

<template>
  <form @submit.prevent="submit">
    <div class="form-group">
      <label>Savol matni</label>
      <textarea v-model="text" required rows="2"></textarea>
    </div>
    <div class="form-group">
      <label>Variantlar (to'g'ri javobni belgilang)</label>
      <div
        v-for="(_, i) in options"
        :key="i"
        style="display: flex; gap: 0.5rem; margin-bottom: 0.4rem; align-items: center;"
      >
        <input type="radio" name="correct-option" :checked="correctIndex === i" @change="correctIndex = i" />
        <input v-model="options[i]" type="text" required style="flex: 1;" :placeholder="`Variant ${i + 1}`" />
        <button v-if="options.length > 2" type="button" class="btn btn-danger" @click="removeOption(i)">X</button>
      </div>
      <button v-if="options.length < 6" type="button" class="btn btn-secondary" @click="addOption">
        + Variant qo'shish
      </button>
    </div>
    <div class="form-group">
      <label>Mavzu (ixtiyoriy)</label>
      <input v-model="topic" type="text" />
    </div>
    <div style="display: flex; gap: 0.5rem;">
      <button class="btn" type="submit">Saqlash</button>
      <button class="btn btn-secondary" type="button" @click="emit('cancel')">Bekor qilish</button>
    </div>
  </form>
</template>
