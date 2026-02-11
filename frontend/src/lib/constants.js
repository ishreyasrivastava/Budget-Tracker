/**
 * App-wide constants and configuration.
 */

export const CATEGORIES = [
  { value: 'Food', label: 'Food', icon: '🍔', color: '#ef4444' },
  { value: 'Transport', label: 'Transport', icon: '🚗', color: '#f59e0b' },
  { value: 'Entertainment', label: 'Entertainment', icon: '🎬', color: '#8b5cf6' },
  { value: 'Bills', label: 'Bills', icon: '📄', color: '#3b82f6' },
  { value: 'Shopping', label: 'Shopping', icon: '🛍️', color: '#ec4899' },
  { value: 'Health', label: 'Health', icon: '💊', color: '#10b981' },
  { value: 'Education', label: 'Education', icon: '📚', color: '#06b6d4' },
  { value: 'Other', label: 'Other', icon: '📦', color: '#6b7280' },
]

export const getCategoryInfo = (category) => {
  return CATEGORIES.find(c => c.value === category) || CATEGORIES[CATEGORIES.length - 1]
}

export const formatCurrency = (amount, currency = 'INR') => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount)
}

export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

export const getCurrentMonth = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

export const getMonthName = (monthStr) => {
  const [year, month] = monthStr.split('-')
  return new Date(year, parseInt(month) - 1).toLocaleDateString('en-IN', {
    month: 'long',
    year: 'numeric'
  })
}
