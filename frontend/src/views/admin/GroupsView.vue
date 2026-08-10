<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { listCourses, type Course } from '../../api/courses'
import { listGroups, createGroup, deleteGroup, listStudents, type Group, type Student } from '../../api/groups'
import StudentImport from '../../components/StudentImport.vue'

const message = useMessage()
const dialog = useDialog()

const courses = ref<Course[]>([])
const selectedCourseId = ref<number | null>(null)
const groups = ref<Group[]>([])
const newGroupName = ref('')

const expandedGroupId = ref<number | null>(null)
const studentsByGroup = ref<Record<number, Student[]>>({})
const studentSortDir = ref<Record<number, 'asc' | 'desc'>>({}) // 'asc' or 'desc' per group

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
    message.error(e?.response?.data?.detail || "Guruhlarni yuklab bo'lmadi")
  }
}

async function addGroup() {
  if (!selectedCourseId.value || !newGroupName.value.trim()) return
  try {
    await createGroup({ course_id: selectedCourseId.value, name: newGroupName.value })
    newGroupName.value = ''
    message.success("Guruh qo'shildi")
    await loadGroups(selectedCourseId.value)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || "Guruh yaratib bo'lmadi")
  }
}

function confirmRemoveGroup(group: Group) {
  dialog.warning({
    title: "Guruhni o'chirish",
    content: `"${group.name}" guruhini o'chirishni tasdiqlaysizmi?`,
    positiveText: "O'chirish",
    negativeText: 'Bekor qilish',
    onPositiveClick: async () => {
      await deleteGroup(group.id)
      message.success("Guruh o'chirildi")
      if (selectedCourseId.value) await loadGroups(selectedCourseId.value)
    },
  })
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

function toggleStudentSort(groupId: number) {
  if (!studentSortDir.value[groupId]) {
    studentSortDir.value[groupId] = 'asc'
  } else {
    studentSortDir.value[groupId] = studentSortDir.value[groupId] === 'asc' ? 'desc' : 'asc'
  }
}

function getSortedStudents(groupId: number) {
  const students = studentsByGroup.value[groupId] || []
  const sortDir = studentSortDir.value[groupId] || 'asc'
  const sorted = [...students].sort((a, b) => {
    const cmp = a.full_name.localeCompare(b.full_name)
    return sortDir === 'asc' ? cmp : -cmp
  })
  return sorted
}
</script>

<template>
  <div>
    <h2>Guruhlar</h2>

    <n-card style="margin-bottom: 1rem;">
      <n-form-item label="Kurs">
        <n-select
          v-model:value="selectedCourseId"
          :options="courses.map((c) => ({ label: c.name, value: c.id }))"
        />
      </n-form-item>
      <n-form-item label="Yangi guruh nomi" style="margin-bottom: 0;">
        <n-input-group>
          <n-input v-model:value="newGroupName" @keyup.enter="addGroup" />
          <n-button type="primary" @click="addGroup">Qo'shish</n-button>
        </n-input-group>
      </n-form-item>
    </n-card>

    <n-card v-for="g in groups" :key="g.id" style="margin-bottom: 1rem;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3 style="margin: 0;">{{ g.name }}</h3>
        <n-space>
          <n-button secondary @click="toggleExpand(g.id)">
            {{ expandedGroupId === g.id ? 'Yopish' : "O'quvchilar" }}
          </n-button>
          <n-button type="error" secondary @click="confirmRemoveGroup(g)">O'chirish</n-button>
        </n-space>
      </div>

      <div v-if="expandedGroupId === g.id" style="margin-top: 1rem; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 1rem;">
        <StudentImport :group-id="g.id" @imported="onStudentsImported(g.id)" />
        <div style="margin-top: 1rem; display: flex; align-items: center; gap: 0.5rem;">
          <n-button
            size="small"
            secondary
            @click="toggleStudentSort(g.id)"
          >
            F.I.Sh {{ studentSortDir[g.id] === 'desc' ? '↓' : '↑' }}
          </n-button>
        </div>
        <n-table style="margin-top: 0.5rem;" single-line>
          <thead>
            <tr><th>F.I.Sh</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in getSortedStudents(g.id)" :key="s.id">
              <td>{{ s.full_name }}</td>
            </tr>
          </tbody>
        </n-table>
        <n-empty v-if="(studentsByGroup[g.id] || []).length === 0" description="Hozircha o'quvchilar yo'q" style="margin-top: 1rem;" />
      </div>
    </n-card>
    <n-empty v-if="groups.length === 0" description="Bu kursda guruhlar yo'q" />
  </div>
</template>
