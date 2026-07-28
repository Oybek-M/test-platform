<script setup lang="ts">
import { watch } from 'vue'
import { darkTheme } from 'naive-ui'
import { useDarkMode } from './composables/useDarkMode'
import { lightThemeOverrides, darkThemeOverrides } from './theme'

const { isDark } = useDarkMode()

// n-global-style resets body's background/text color only once on its first
// mount and then keeps re-applying that same stale value on every later theme
// toggle, fighting any reactive update (naive-ui limitation) — so the page
// background is owned and kept in sync with the current theme here instead.
watch(
  isDark,
  (value) => {
    const overrides = value ? darkThemeOverrides : lightThemeOverrides
    document.body.style.backgroundColor = overrides.common!.bodyColor!
    document.body.style.color = value ? 'rgba(255, 255, 255, 0.82)' : 'rgb(51, 54, 57)'
  },
  { immediate: true },
)
</script>

<template>
  <n-config-provider
    :theme="isDark ? darkTheme : null"
    :theme-overrides="isDark ? darkThemeOverrides : lightThemeOverrides"
  >
    <n-message-provider>
      <n-dialog-provider>
        <router-view v-slot="{ Component }">
          <component :is="Component" :key="isDark ? 'dark' : 'light'" />
        </router-view>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
