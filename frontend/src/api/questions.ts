import client from './client'

export interface Question {
  id: number
  course_id: number
  text: string
  options: string[]
  correct_index: number
  topic: string | null
  is_active: boolean
}

export async function listQuestions(
  courseId: number,
  params?: { topic?: string; is_active?: boolean },
): Promise<Question[]> {
  const resp = await client.get(`/admin/courses/${courseId}/questions`, { params })
  return resp.data
}

export async function createQuestion(
  courseId: number,
  payload: { text: string; options: string[]; correct_index: number; topic?: string },
): Promise<Question> {
  const resp = await client.post(`/admin/courses/${courseId}/questions`, payload)
  return resp.data
}

export async function updateQuestion(
  courseId: number,
  questionId: number,
  payload: Partial<{ text: string; options: string[]; correct_index: number; topic: string; is_active: boolean }>,
): Promise<Question> {
  const resp = await client.put(`/admin/courses/${courseId}/questions/${questionId}`, payload)
  return resp.data
}

export async function deleteQuestion(courseId: number, questionId: number): Promise<void> {
  await client.delete(`/admin/courses/${courseId}/questions/${questionId}`)
}

export interface QuestionImportPreview {
  questions_found: number
  errors: string[]
  preview: Array<{ text: string; options: string[]; correct_index: number; topic: string | null }>
}

export interface QuestionImportResult {
  imported: number
}

export async function importQuestions(
  courseId: number,
  file: File,
  confirm: boolean,
): Promise<QuestionImportPreview | QuestionImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('confirm', String(confirm))
  const resp = await client.post(`/admin/courses/${courseId}/questions/import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return resp.data
}

export function sampleQuestionsUrl(): string {
  return '/api/admin/samples/questions.xlsx'
}
