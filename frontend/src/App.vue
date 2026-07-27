<script setup lang="ts">
import { darkTheme } from 'naive-ui'
import { useDarkMode } from './composables/useDarkMode'
import { lightThemeOverrides, darkThemeOverrides } from './theme'

const { isDark } = useDarkMode()
</script>

<template>
  <n-config-provider
    :theme="isDark ? darkTheme : null"
    :theme-overrides="isDark ? darkThemeOverrides : lightThemeOverrides"
  >
    <n-global-style />
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
