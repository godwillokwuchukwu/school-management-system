const API_URL = import.meta.env.VITE_API_URL || '/api'
const ACCESS_TOKEN_KEY = 'applicant_access_token'
const REFRESH_TOKEN_KEY = 'applicant_refresh_token'

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY) || localStorage.getItem('access_token')
}

function saveTokens(data) {
  if (data.access) {
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access)
    localStorage.setItem('access_token', data.access)
  }
  if (data.refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh)
    localStorage.setItem('refresh_token', data.refresh)
  }
}

function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
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
  const isPublicRoute = path.startsWith('/public/') || path.startsWith('/auth/')
  if (token && (!isPublicRoute || options.requiresAuth)) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (response.status === 401) {
    if (canRefresh && (await refreshAccessToken())) {
      return request(path, options, false)
    }
    clearTokens()
    if (isPublicRoute && !options.requiresAuth) {
      headers.delete('Authorization')
      const retryResp = await fetch(`${API_URL}${path}`, { ...options, headers })
      const retryPayload = retryResp.status === 204 ? null : await retryResp.json().catch(() => null)
      if (retryResp.ok) return retryPayload
    }
  }

  const payload = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status === 401) {
      clearTokens()
    }
    let detail = ''
    if (payload) {
      if (payload.detail) {
        detail = String(payload.detail)
      } else if (payload.non_field_errors) {
        detail = [].concat(payload.non_field_errors).join(' ')
      } else if (payload.message) {
        detail = String(payload.message)
      } else {
        // Collect all field-level validation errors
        const fieldErrors = Object.entries(payload)
          .map(([key, val]) => {
            const msgs = [].concat(val).map(String).join(', ')
            return `${key}: ${msgs}`
          })
          .join('; ')
        detail = fieldErrors || `Request failed (${response.status})`
      }
    } else {
      detail = `Request failed (${response.status})`
    }
    throw new ApiError(detail, response.status, payload)
  }
  return payload
}

function list(payload) {
  return Array.isArray(payload) ? payload : payload?.results || []
}

export const publicApi = {
  isAuthenticated: () => Boolean(getAccessToken()),
  logout: clearTokens,

  // --- Student Portal Auth ---
  async studentRegister(body) {
    return request('/auth/student/register/', { method: 'POST', body: JSON.stringify(body) }, false)
  },
  async verifyEmail(token) {
    return request(`/auth/verify-email/${token}/`, {}, false)
  },
  async resendVerification(email) {
    return request('/auth/resend-verification/', { method: 'POST', body: JSON.stringify({ email }) }, false)
  },
  async requestPasswordReset(email) {
    return request('/auth/password-reset/', { method: 'POST', body: JSON.stringify({ email }) }, false)
  },
  async getNotifications() {
    return request('/accounts/notifications/')
  },

  // --- Applicant account ---
  async register(body) {
    return request('/auth/register/', { method: 'POST', body: JSON.stringify(body) }, false)
  },
  async login(username, password) {
    const data = await request('/auth/login/', { method: 'POST', body: JSON.stringify({ username, password }) }, false)
    saveTokens(data)
    return data
  },

  // --- Public marketing content (unauthenticated) ---
  school: () => request('/public/school/'),
  news: (query = '') => request(`/public/news/${query}`),
  newsArticle: (slug) => request(`/public/news/${slug}/`),
  events: (query = '') => request(`/public/events/${query}`),
  event: (slug) => request(`/public/events/${slug}/`),
  programs: (query = '') => request(`/public/programs/${query}`),
  testimonials: () => request('/public/testimonials/'),
  faqs: (query = '') => request(`/public/faqs/${query}`),
  jobs: (query = '') => request(`/public/careers/jobs/${query}`),

  // --- Public write endpoints (rate-limited server-side) ---
  submitContact: (body) => request('/public/contact/', { method: 'POST', body: JSON.stringify(body) }, false),
  submitAdmissionEnquiry: (body) => request('/public/admissions/enquiries/', { method: 'POST', body: JSON.stringify(body) }, false),
  admissionEnquiryStatus: (reference) => request(`/public/admissions/enquiries/${encodeURIComponent(reference)}/`, {}, false),
  applyForJob: (formData) => request('/public/careers/apply/', { method: 'POST', body: formData }, false),

  // --- Full admission application (requires an Applicant account) ---
  myApplications: () => request('/admissions/applications/').then(list),
  application: (id) => request(`/admissions/applications/${id}/`),
  createApplication: (body) => request('/admissions/applications/', { method: 'POST', body: JSON.stringify(body) }),
  updateApplication: (id, body) => request(`/admissions/applications/${id}/`, { method: 'PATCH', body: JSON.stringify(body) }),
  submitApplication: (id) => request(`/admissions/applications/${id}/submit/`, { method: 'POST' }),
  uploadApplicationDocument: (id, formData) => request(`/admissions/applications/${id}/documents/`, { method: 'POST', body: formData }),
  applicationDocuments: (id) => request(`/admissions/applications/${id}/documents/`).then(list),
  applicationStatus: (reference) => request(`/admissions/status/${encodeURIComponent(reference)}/`, {}, false),
  jobApplicationStatus: (reference) => request(`/public/careers/applications/${encodeURIComponent(reference)}/`, {}, false),

  // --- Parent/guardian relationship request (Section 2.6/23) ---
  myParentRelationshipRequests: () => request('/admissions/parent-relationships/').then(list),
  createParentRelationshipRequest: (body) => request('/admissions/parent-relationships/', { method: 'POST', body: JSON.stringify(body) }),
}

export { API_URL, list }
