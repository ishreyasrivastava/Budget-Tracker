/**
 * Expenses page with full CRUD functionality.
 */

import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { 
  CATEGORIES, 
  formatCurrency, 
  formatDate, 
  getCategoryInfo,
  getCurrentMonth 
} from '../lib/constants'
import { 
  Plus, 
  Search, 
  Filter, 
  Edit2, 
  Trash2, 
  X,
  Loader2,
  Calendar
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Expenses() {
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingExpense, setEditingExpense] = useState(null)
  const [filters, setFilters] = useState({
    category: '',
    month: getCurrentMonth()
  })
  const [formData, setFormData] = useState({
    amount: '',
    category: 'Food',
    description: '',
    date: new Date().toISOString().split('T')[0]
  })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchExpenses()
  }, [filters])

  const fetchExpenses = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.category) params.category = filters.category
      if (filters.month) params.month = filters.month
      
      const data = await api.getExpenses(params)
      setExpenses(data.expenses || [])
    } catch (error) {
      toast.error('Failed to load expenses')
    } finally {
      setLoading(false)
    }
  }

  const openModal = (expense = null) => {
    if (expense) {
      setEditingExpense(expense)
      setFormData({
        amount: expense.amount.toString(),
        category: expense.category,
        description: expense.description || '',
        date: expense.date
      })
    } else {
      setEditingExpense(null)
      setFormData({
        amount: '',
        category: 'Food',
        description: '',
        date: new Date().toISOString().split('T')[0]
      })
    }
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingExpense(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      toast.error('Please enter a valid amount')
      return
    }

    setSubmitting(true)
    try {
      const payload = {
        amount: parseFloat(formData.amount),
        category: formData.category,
        description: formData.description || null,
        date: formData.date
      }

      if (editingExpense) {
        await api.updateExpense(editingExpense.id, payload)
        toast.success('Expense updated')
      } else {
        await api.createExpense(payload)
        toast.success('Expense added')
      }

      closeModal()
      fetchExpenses()
    } catch (error) {
      toast.error(error.message || 'Failed to save expense')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this expense?')) return

    try {
      await api.deleteExpense(id)
      toast.success('Expense deleted')
      fetchExpenses()
    } catch (error) {
      toast.error('Failed to delete expense')
    }
  }

  const totalAmount = expenses.reduce((sum, e) => sum + e.amount, 0)

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-dark-100">Expenses</h1>
          <p className="text-dark-500 mt-1">Track and manage your spending</p>
        </div>
        <button
          onClick={() => openModal()}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Expense
        </button>
      </div>

      {/* Filters */}
      <div className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm text-dark-500 mb-2">Month</label>
            <input
              type="month"
              value={filters.month}
              onChange={(e) => setFilters({ ...filters, month: e.target.value })}
              className="input-field"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm text-dark-500 mb-2">Category</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="input-field"
            >
              <option value="">All Categories</option>
              {CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.icon} {cat.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="glass-card p-4 flex items-center justify-between">
        <div>
          <span className="text-dark-500">Total for period:</span>
          <span className="text-dark-100 font-bold text-xl ml-2">
            {formatCurrency(totalAmount)}
          </span>
        </div>
        <span className="text-dark-500">{expenses.length} expenses</span>
      </div>

      {/* Expenses List */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="p-12 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
          </div>
        ) : expenses.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-16 h-16 rounded-full bg-dark-800 flex items-center justify-center mx-auto mb-4">
              <Receipt className="w-8 h-8 text-dark-500" />
            </div>
            <p className="text-dark-400 text-lg">No expenses found</p>
            <p className="text-dark-600 mt-1">Add your first expense to get started</p>
          </div>
        ) : (
          <div className="divide-y divide-dark-800">
            {expenses.map((expense) => {
              const catInfo = getCategoryInfo(expense.category)
              return (
                <div 
                  key={expense.id}
                  className="p-4 flex items-center gap-4 hover:bg-dark-800/30 transition-colors"
                >
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                    style={{ backgroundColor: `${catInfo.color}20` }}
                  >
                    {catInfo.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-dark-100 font-medium truncate">
                      {expense.description || expense.category}
                    </p>
                    <div className="flex items-center gap-2 text-sm text-dark-500">
                      <span 
                        className="px-2 py-0.5 rounded-full text-xs"
                        style={{ 
                          backgroundColor: `${catInfo.color}20`,
                          color: catInfo.color
                        }}
                      >
                        {expense.category}
                      </span>
                      <span>•</span>
                      <span>{formatDate(expense.date)}</span>
                    </div>
                  </div>
                  <span className="text-dark-100 font-bold text-lg">
                    {formatCurrency(expense.amount)}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => openModal(expense)}
                      className="p-2 text-dark-500 hover:text-primary-400 hover:bg-dark-800 rounded-lg transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(expense.id)}
                      className="p-2 text-dark-500 hover:text-danger hover:bg-dark-800 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="glass-card w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-dark-100">
                {editingExpense ? 'Edit Expense' : 'Add Expense'}
              </h2>
              <button
                onClick={closeModal}
                className="p-2 text-dark-500 hover:text-dark-100 hover:bg-dark-800 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-dark-400 mb-2">Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="input-field"
                  placeholder="0.00"
                  required
                />
              </div>

              <div>
                <label className="block text-sm text-dark-400 mb-2">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="input-field"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.icon} {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-dark-400 mb-2">Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="input-field"
                  placeholder="What was this expense for?"
                />
              </div>

              <div>
                <label className="block text-sm text-dark-400 mb-2">Date</label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="input-field"
                  required
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={closeModal}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    editingExpense ? 'Update' : 'Add Expense'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

// Missing import fix
function Receipt(props) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1-2-1Z"/>
      <path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/>
      <path d="M12 17.5v-11"/>
    </svg>
  )
}
