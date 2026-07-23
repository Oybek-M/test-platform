import client from './client'

export interface GradeBand {
  grade: string
  min: number
}

export interface Course {
  id: number
  name: string
  description: string | null
  grading_scale: GradeBand[]
}

export async function listCourses(): Promise<Course[]> {
  const resp = await client.get('/admin/courses')
  return resp.data
}

export async function createCourse(payload: {
  name: string
  description?: string
  grading_scale?: GradeBand[]
}): Promise<Course> {
  const resp = await client.post('/admin/courses', payload)
  return resp.data
}

export async function updateCourse(
  id: number,
  payload: Partial<{ name: string; description: string; grading_scale: GradeBand[] }>,
): Promise<Course> {
  const resp = await client.put(`/admin/courses/${id}`, payload)
  return resp.data
}

export async function deleteCourse(id: number): Promise<void> {
  await client.delete(`/admin/courses/${id}`)
}
