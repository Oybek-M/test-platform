import client from './client'

export interface Group {
  id: number
  course_id: number
  name: string
}

export async function listGroups(courseId?: number): Promise<Group[]> {
  const resp = await client.get('/admin/groups', { params: courseId ? { course_id: courseId } : {} })
  return resp.data
}

export async function createGroup(payload: { course_id: number; name: string }): Promise<Group> {
  const resp = await client.post('/admin/groups', payload)
  return resp.data
}

export async function updateGroup(id: number, payload: { name: string }): Promise<Group> {
  const resp = await client.put(`/admin/groups/${id}`, payload)
  return resp.data
}

export async function deleteGroup(id: number): Promise<void> {
  await client.delete(`/admin/groups/${id}`)
}

export interface Student {
  id: number
  group_id: number
  full_name: string
}

export interface StudentImportResult {
  created: Student[]
  warnings: string[]
}

export async function listStudents(groupId: number): Promise<Student[]> {
  const resp = await client.get(`/admin/groups/${groupId}/students`)
  return resp.data
}

export async function addStudentsFromText(groupId: number, text: string): Promise<StudentImportResult> {
  const resp = await client.post(`/admin/groups/${groupId}/students`, { text })
  return resp.data
}

export async function addStudentsFromXlsx(groupId: number, file: File): Promise<StudentImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const resp = await client.post(`/admin/groups/${groupId}/students/import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return resp.data
}

export function sampleStudentsUrl(): string {
  return '/api/admin/samples/students.xlsx'
}
