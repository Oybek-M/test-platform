<script setup lang="ts">
defineEmits<{ close: [] }>()
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card card">
      <slot />
    </div>
  </div>
</template>
