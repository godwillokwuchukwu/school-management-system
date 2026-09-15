const API_URL =
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' &&
  window.location.hostname !== 'localhost' &&
  window.location.hostname !== '127.0.0.1'
    ? '/api'
    : 'http://localhost:8000/api')
const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

function saveTokens(data) {
  if (data.access) localStorage.setItem(ACCESS_TOKEN_KEY, data.access)
  if (data.refresh) localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh)
}

function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
  if (!refresh) return false
  const response = await fetch(`${API_URL}/auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!response.ok) {
    clearTokens()
    return false
  }
  saveTokens(await response.json())
  return true
}

async function request(path, options = {}, canRefresh = true) {
  const headers = new Headers(options.headers || {})
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (response.status === 401 && canRefresh && await refreshAccessToken()) {
    return request(path, options, false)
  }

  const payload = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) {
    const detail = payload?.detail || Object.values(payload || {})?.flat?.()?.[0] || `Request failed (${response.status})`
    throw new ApiError(String(detail), response.status, payload)
  }
  return payload
}

function list(payload) {
  return Array.isArray(payload) ? payload : payload?.results || []
}

const api = {
  isAuthenticated: () => Boolean(getAccessToken()),
  logout: clearTokens,
  async login(username, password) {
    const data = await request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }, false)
    saveTokens(data)
    return data
  },
  register: (body) => request('/auth/register/', { method: 'POST', body: JSON.stringify(body) }, false),
  requestPasswordReset: (email) => request('/auth/password-reset/', { method: 'POST', body: JSON.stringify({ email }) }, false),
  confirmPasswordReset: (body) => request('/auth/password-reset/confirm/', { method: 'POST', body: JSON.stringify(body) }, false),
  profile: () => request('/accounts/profiles/me/'),
  updateProfile: (body) => request('/accounts/profiles/me/', { method: 'PATCH', body: JSON.stringify(body) }),
  subjects: (query = '') => request(`/academics/subjects/${query}`),
  classes: (query = '') => request(`/academics/classes/${query}`),
  enrollments: (query = '') => request(`/academics/enrollments/${query}`),
  grades: (query = '') => request(`/academics/grades/${query}`),
  attendance: (query = '') => request(`/attendance/records/${query}`),
  assignments: (query = '') => request(`/activities/assignments/${query}`),
  createAssignment: (body) => request('/activities/assignments/', { method: 'POST', body: JSON.stringify(body) }),
  submissions: (query = '') => request(`/activities/submissions/${query}`),
  announcements: (query = '') => request(`/communications/announcements/${query}`),
  conversations: (query = '') => request(`/communications/conversations/${query}`),
  replyToConversation: (id, body) => request(`/communications/conversations/${id}/reply/`, { method: 'POST', body: JSON.stringify({ body }) }),
  markMessageRead: (id) => request(`/communications/conversations/${id}/mark_read/`, { method: 'POST' }),
  createConversation: (body) => request('/communications/conversations/', { method: 'POST', body: JSON.stringify(body) }),
  createAnnouncement: (body) => request('/communications/announcements/', { method: 'POST', body: JSON.stringify(body) }),
  
  // Documents
  documents: (query = '') => request(`/core/documents/${query}`),
  
  // Activities (Events, Meetings)
  events: (query = '') => request(`/activities/events/${query}`),
  meetings: (query = '') => request(`/activities/meetings/${query}`),
  
  // AI Assistants
  aiChatbot: (prompt) => request('/ai/chatbot/', { method: 'POST', body: JSON.stringify({ prompt }) }),
  aiTeacher: (prompt) => request('/ai/teacher/', { method: 'POST', body: JSON.stringify({ prompt }) }),
  aiAdmin: (prompt) => request('/ai/admin/', { method: 'POST', body: JSON.stringify({ prompt }) }),
  aiExplainer: (prompt) => request('/ai/explainer/', { method: 'POST', body: JSON.stringify({ prompt }) }),
  
  createSubmission: (body) => request('/activities/submissions/', { method: 'POST', body: JSON.stringify(body) }),
  bulkMarkAttendance: (records) => request('/attendance/records/bulk_mark/', { method: 'POST', body: JSON.stringify({ records }) }),
  fees: (query = '') => request(`/fees/fees/${query}`),
  createFee: (body) => request('/fees/fees/', { method: 'POST', body: JSON.stringify(body) }),
  updateFee: (id, body) => request(`/fees/fees/${id}/`, { method: 'PATCH', body: JSON.stringify(body) }),
  reports: (query = '') => request(`/reporting/reports/${query}`),
  students: (query = '') => request(`/students/students/${query}`),
  children: () => request('/students/students/children/'),
  studentRecipients: () => request('/students/students/recipients/'),
  createStudent: (body) => { const parts = (body.name || `${body.first_name || ''} ${body.last_name || ''}`).trim().split(/\s+/); return request('/students/students/', { method: 'POST', body: JSON.stringify({ ...body, first_name: body.first_name || parts.shift(), last_name: body.last_name || parts.join(' '), admission_number: body.admission_number || body.admission, dob: body.dob || '2010-01-01' }) }) },
  updateStudent: (id, body) => request(`/students/students/${id}/`, { method: 'PATCH', body: JSON.stringify(body) }),
  
  activateAccount: (token, password) => request('/auth/activate/', { method: 'POST', body: JSON.stringify({ token, password }) }),
  adminProvisionAccount: (data) => request('/accounts/admin/provision/', { method: 'POST', body: JSON.stringify(data) }),
  adminSuspendProfile: (id) => request(`/accounts/profiles/${id}/suspend/`, { method: 'POST' }),
  adminReactivateProfile: (id) => request(`/accounts/profiles/${id}/reactivate/`, { method: 'POST' }),

  deleteStudent: (id) => request(`/students/students/${id}/`, { method: 'DELETE' }),
  async dashboard() {
    const results = await Promise.allSettled([
      this.profile(), this.classes(), this.enrollments(), this.attendance(),
      this.assignments(), this.announcements(), this.conversations(), this.reports(), this.subjects(), this.grades(),
      this.students(), this.submissions(), this.children(), this.documents(), this.studentRecipients(), this.fees(),
      this.events(), this.meetings()
    ])
    const [profile, classes, enrollments, attendance, assignments, announcements, conversations, reports, subjects, grades, students, submissions, children, documents, studentRecipients, fees, events, meetings] = results.map((result) => result.status === 'fulfilled' ? result.value : [])
    return {
      profile: profile && !Array.isArray(profile) ? profile : null,
      classes: list(classes),
      enrollments: list(enrollments),
      attendance: list(attendance),
      assignments: list(assignments),
      announcements: list(announcements),
      conversations: list(conversations),
      reports: list(reports),
      subjects: list(subjects),
      grades: list(grades),
      students: list(students),
      submissions: list(submissions),
      children: list(children),
      documents: list(documents),
      studentRecipients: list(studentRecipients),
      fees: list(fees),
      events: list(events),
      meetings: list(meetings),
    }
  },
}

export { api, API_URL, list }
export default api

