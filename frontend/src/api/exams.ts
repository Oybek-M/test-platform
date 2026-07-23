import client from './client'

export interface Exam {
  id: number
  course_id: number
  group_id: number
  title: string
  starts_at: string
  duration_minutes: number
  question_count: number
  shuffle_questions: boolean
  shuffle_options: boolean
  allow_resume: boolean
  show_result_to_student: boolean
  totp_digits: number
  totp_period: number
  status: string
  access_code: string
}

export interface ExamCreatePayload {
  course_id: number
  group_id: number
  title: string
  starts_at: string
  duration_minutes: number
  question_count: number
  shuffle_questions?: boolean
  shuffle_options?: boolean
  allow_resume?: boolean
  show_result_to_student?: boolean
  totp_digits?: number
  totp_period?: number
}

export async function listExams(params?: { course_id?: number; group_id?: number }): Promise<Exam[]> {
  const resp = await client.get('/admin/exams', { params })
  return resp.data
}

export async function createExam(payload: ExamCreatePayload): Promise<Exam> {
  const resp = await client.post('/admin/exams', payload)
  return resp.data
}

export async function getExam(id: number): Promise<Exam> {
  const resp = await client.get(`/admin/exams/${id}`)
  return resp.data
}

export async function updateExam(id: number, payload: Partial<ExamCreatePayload>): Promise<Exam> {
  const resp = await client.put(`/admin/exams/${id}`, payload)
  return resp.data
}

export async function deleteExam(id: number): Promise<void> {
  await client.delete(`/admin/exams/${id}`)
}

export async function setExamStatus(id: number, status: string): Promise<Exam> {
  const resp = await client.post(`/admin/exams/${id}/status`, { status })
  return resp.data
}

export async function getLiveTotp(id: number): Promise<{ code: string; seconds_left: number }> {
  const resp = await client.get(`/admin/exams/${id}/totp`)
  return resp.data
}

export interface AttemptResult {
  student_id: number
  student_name: string
  score: number | null
  total: number | null
  percent: number | null
  grade: string | null
  started_at: string
  submitted_at: string | null
  status: string
}

export async function getExamResults(id: number): Promise<AttemptResult[]> {
  const resp = await client.get(`/admin/exams/${id}/results`)
  return resp.data
}
