<script setup lang="ts">
import { useExamStore } from '../../stores/exam'

const examStore = useExamStore()
const result = examStore.result
</script>

<template>
  <div class="container" style="max-width: 420px; padding-top: 3rem; text-align: center;">
    <div class="card">
      <h2>Imtihon yakunlandi</h2>
      <template v-if="result && result.percent !== undefined">
        <p style="font-size: 2.5rem; font-weight: 700;">{{ result.percent }}%</p>
        <p class="muted">{{ result.score }} / {{ result.total }} to'g'ri javob</p>
        <p style="font-size: 1.5rem; font-weight: 600;">Baho: {{ result.grade }}</p>
      </template>
      <template v-else>
        <p>Javoblaringiz qabul qilindi. Natijangiz keyinroq e'lon qilinadi.</p>
      </template>
    </div>
  </div>
</template>
