<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { listCourses, type Course } from '../../api/courses'
import { listGroups, createGroup, deleteGroup, listStudents, type Group, type Student } from '../../api/groups'
import StudentImport from '../../components/StudentImport.vue'

const courses = ref<Course[]>([])
const selectedCourseId = ref<number | null>(null)
const groups = ref<Group[]>([])
const error = ref('')
const newGroupName = ref('')

const expandedGroupId = ref<number | null>(null)
const studentsByGroup = ref<Record<number, Student[]>>({})

onMounted(async () => {
  courses.value = await listCourses()
  if (courses.value.length) {
    selectedCourseId.value = courses.value[0].id
  }
})

watch(selectedCourseId, async (id) => {
  if (id) await loadGroups(id)
})

async function loadGroups(courseId: number) {
  try {
    groups.value = await listGroups(courseId)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Guruhlarni yuklab bo'lmadi"
  }
}

async function addGroup() {
  if (!selectedCourseId.value || !newGroupName.value.trim()) return
  await createGroup({ course_id: selectedCourseId.value, name: newGroupName.value })
  newGroupName.value = ''
  await loadGroups(selectedCourseId.value)
}

async function removeGroup(id: number) {
  if (!confirm("Guruhni o'chirishni tasdiqlaysizmi?")) return
  await deleteGroup(id)
  if (selectedCourseId.value) await loadGroups(selectedCourseId.value)
}

async function toggleExpand(groupId: number) {
  if (expandedGroupId.value === groupId) {
    expandedGroupId.value = null
    return
  }
  expandedGroupId.value = groupId
  await loadStudents(groupId)
}

async function loadStudents(groupId: number) {
  studentsByGroup.value[groupId] = await listStudents(groupId)
}

function onStudentsImported(groupId: number) {
  loadStudents(groupId)
}
</script>

<template>
  <div>
    <h2>Guruhlar</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="card">
      <div class="form-group">
        <label>Kurs</label>
        <select v-model.number="selectedCourseId">
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <form @submit.prevent="addGroup" style="display: flex; gap: 0.5rem; align-items: end;">
        <div class="form-group" style="margin-bottom: 0; flex: 1;">
          <label>Yangi guruh nomi</label>
          <input v-model="newGroupName" type="text" required />
        </div>
        <button class="btn" type="submit">Qo'shish</button>
      </form>
    </div>

    <div v-for="g in groups" :key="g.id" class="card">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3>{{ g.name }}</h3>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-secondary" @click="toggleExpand(g.id)">
            {{ expandedGroupId === g.id ? 'Yopish' : "O'quvchilar" }}
          </button>
          <button class="btn btn-danger" @click="removeGroup(g.id)">O'chirish</button>
        </div>
      </div>

      <div
        v-if="expandedGroupId === g.id"
        style="margin-top: 1rem; border-top: 1px solid var(--color-border); padding-top: 1rem;"
      >
        <StudentImport :group-id="g.id" @imported="onStudentsImported(g.id)" />
        <table style="margin-top: 1rem;">
          <thead>
            <tr>
              <th>F.I.Sh</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in studentsByGroup[g.id] || []" :key="s.id">
              <td>{{ s.full_name }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="(studentsByGroup[g.id] || []).length === 0" class="muted">Hozircha o'quvchilar yo'q.</p>
      </div>
    </div>
    <p v-if="groups.length === 0" class="muted">Bu kursda guruhlar yo'q.</p>
  </div>
</template>
