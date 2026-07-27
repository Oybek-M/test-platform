import { ref, watch } from 'vue'
import { useOsTheme } from 'naive-ui'

const STORAGE_KEY = 'test-platform-theme'
const osTheme = useOsTheme()

function getInitialValue(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'dark') return true
  if (stored === 'light') return false
  return osTheme.value === 'dark'
}

const isDark = ref(getInitialValue())

watch(isDark, (value) => {
  localStorage.setItem(STORAGE_KEY, value ? 'dark' : 'light')
})

export function useDarkMode() {
  function toggle() {
    isDark.value = !isDark.value
  }
  return { isDark, toggle }
}
