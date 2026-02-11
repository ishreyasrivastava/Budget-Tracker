/**
 * API client for Budget Tracker backend.
 * Handles all HTTP requests with authentication.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  constructor() {
    this.baseUrl = API_URL
    this.token = null
  }

  setToken(token) {
    this.token = token
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}/api${endpoint}`
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      if (response.status === 204) {
        return null
      }

      return await response.json()
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error)
      throw error
    }
  }

  // Auth endpoints
  async signup(email, password, fullName) {
    return this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    })
  }

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  }

  async logout() {
    return this.request('/auth/logout', { method: 'POST' })
  }

  async getMe() {
    return this.request('/auth/me')
  }

  // Expense endpoints
  async getExpenses(params = {}) {
    const searchParams = new URLSearchParams()
    if (params.category) searchParams.append('category', params.category)
    if (params.month) searchParams.append('month', params.month)
    if (params.startDate) searchParams.append('start_date', params.startDate)
    if (params.endDate) searchParams.append('end_date', params.endDate)
    if (params.limit) searchParams.append('limit', params.limit)
    if (params.offset) searchParams.append('offset', params.offset)
    
    const query = searchParams.toString()
    return this.request(`/expenses/${query ? `?${query}` : ''}`)
  }

  async createExpense(expense) {
    return this.request('/expenses/', {
      method: 'POST',
      body: JSON.stringify(expense),
    })
  }

  async updateExpense(id, expense) {
    return this.request(`/expenses/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(expense),
    })
  }

  async deleteExpense(id) {
    return this.request(`/expenses/${id}`, { method: 'DELETE' })
  }

  // Budget endpoints
  async getBudgets(params = {}) {
    const searchParams = new URLSearchParams()
    if (params.month) searchParams.append('month', params.month)
    if (params.category) searchParams.append('category', params.category)
    
    const query = searchParams.toString()
    return this.request(`/budgets/${query ? `?${query}` : ''}`)
  }

  async createBudget(budget) {
    return this.request('/budgets/', {
      method: 'POST',
      body: JSON.stringify(budget),
    })
  }

  async updateBudget(id, budget) {
    return this.request(`/budgets/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(budget),
    })
  }

  async deleteBudget(id) {
    return this.request(`/budgets/${id}`, { method: 'DELETE' })
  }

  // Dashboard endpoints
  async getDashboard(month) {
    const params = month ? `?month=${month}` : ''
    return this.request(`/dashboard/${params}`)
  }

  async getAlerts() {
    return this.request('/dashboard/alerts')
  }
}

export const api = new ApiClient()
