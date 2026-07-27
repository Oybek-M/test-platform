<script setup lang="ts">
import { useExamStore } from '../../stores/exam'

const examStore = useExamStore()
const result = examStore.result
</script>

<template>
  <div style="max-width: 420px; margin: 0 auto; padding: 3rem 1.5rem 1.5rem; text-align: center;">
    <n-card title="Imtihon yakunlandi">
      <template v-if="result && result.percent !== undefined">
        <p style="font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0;">{{ result.percent }}%</p>
        <p style="color: var(--n-text-color-3, #6b7280);">{{ result.score }} / {{ result.total }} to'g'ri javob</p>
        <p style="font-size: 1.5rem; font-weight: 600;">Baho: {{ result.grade }}</p>
      </template>
      <template v-else>
        <p>Javoblaringiz qabul qilindi. Natijangiz keyinroq e'lon qilinadi.</p>
      </template>
    </n-card>
  </div>
</template>
