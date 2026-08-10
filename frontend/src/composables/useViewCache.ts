import { ref, watch, type Ref } from 'vue'

/**
 * Module-level caches that survive component remounting (used for theme toggle remounting)
 * This allows data to persist across component destruction/recreation while still allowing
 * background refreshes (onMounted) to keep data current.
 */
const valueCache = new Map<string, unknown>()
const refCache = new Map<string, Ref<unknown>>()

/**
 * Create a reactive ref that persists its value across component remounts via an external cache.
 *
 * Usage:
 *   const groups = useViewCache<Group[]>('groups:courseId123', [])
 *
 * On first mount, the ref is populated from cache if available, otherwise uses initial value.
 * On every value change, it updates the cache automatically (via watch with deep: true).
 * When the component remounts (due to theme toggle), the cache survives, so the new instance
 * gets the previous data immediately — no flash or empty state.
 *
 * The same Ref is returned for the same key, so watchers and reactivity work across remounts.
 *
 * @param key - Unique cache key (should incorporate any filter/param dependencies, e.g. "groups:courseId123")
 * @param initial - Initial value if not in cache
 * @returns Ref with persisted value
 */
export function useViewCache<T>(key: string, initial: T): Ref<T> {
  // Return existing Ref if this key has been used before (e.g., after remount)
  if (refCache.has(key)) {
    return refCache.get(key) as Ref<T>
  }

  // Create new Ref with cached value or initial value
  const value = ref<T>((valueCache.has(key) ? valueCache.get(key) : initial) as T)

  // Watch for changes and update the value cache
  watch(value, (v) => valueCache.set(key, v), { deep: true })

  // Cache the Ref itself so we return the same instance on subsequent calls
  refCache.set(key, value)

  return value as Ref<T>
}
