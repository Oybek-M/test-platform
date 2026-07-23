import axios from 'axios'

// Public, unauthenticated client for the student exam flow - deliberately
// separate from the admin `client` so no admin JWT is ever attached here.
const examClient = axios.create({ baseURL: '/api/exam' })

export interface ExamPublicStatus {
  title: string
  group_name: string
  status: string
  starts_at: string
  duration_minutes: number
  is_open_now: boolean
}

export async function getExamStatus(accessCode: string): Promise<ExamPublicStatus> {
  const resp = await examClient.get(`/${accessCode}`)
  return resp.data
}

export async function verifyCode(accessCode: string, code: string): Promise<boolean> {
  const resp = await examClient.post(`/${accessCode}/verify-code`, { code })
  return resp.data.ok
}

export interface StudentPublic {
  id: number
  full_name: string
}

export async function listAvailableStudents(accessCode: string, code: string): Promise<StudentPublic[]> {
  const resp = await examClient.get(`/${accessCode}/students`, { params: { code } })
  return resp.data
}

export interface PublicQuestion {
  id: number
  text: string
  options: string[]
}

export interface StartExamResult {
  attempt_id: number
  ends_at: string
  questions: PublicQuestion[]
}

export async function startExam(accessCode: string, studentId: number, code: string): Promise<StartExamResult> {
  const resp = await examClient.post(`/${accessCode}/start`, { student_id: studentId, code })
  return resp.data
}

export interface SubmitResult {
  score?: number
  total?: number
  percent?: number
  grade?: string
  submitted?: boolean
}

export async function submitExam(
  accessCode: string,
  attemptId: number,
  answers: Record<number, number>,
): Promise<SubmitResult> {
  const resp = await examClient.post(`/${accessCode}/submit`, { attempt_id: attemptId, answers })
  return resp.data
}
