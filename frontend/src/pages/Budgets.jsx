/**
 * Budgets page for setting and tracking monthly budgets.
 */

import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { 
  CATEGORIES, 
  formatCurrency, 
  getCategoryInfo,
  getCurrentMonth,
  getMonthName 
} from '../lib/constants'
import { 
  Plus, 
  Edit2, 
  Trash2, 
  X,
  Loader2,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Budgets() {
  const [budgets, setBudgets] = useState([])
  const [loading, setLoading] = useState(true)
  const [month, setMonth] = useState(getCurrentMonth())
  const [modalOpen, setModalOpen] = useState(false)
  const [editingBudget, setEditingBudget] = useState(null)
  const [formData, setFormData] = useState({
    category: 'Food',
    amount: ''
  })
  const [submitting, setSubmitting] = useState(false)
  const [totalBudget, setTotalBudget] = useState(0)
  const [totalSpent, setTotalSpent] = useState(0)

  useEffect(() => {
    fetchBudgets()
  }, [month])

  const fetchBudgets = async () => {
    setLoading(true)
    try {
      const data = await api.getBudgets({ month })
      setBudgets(data.budgets || [])
      setTotalBudget(data.total_budget || 0)
      setTotalSpent(data.total_spent || 0)
    } catch (error) {
      toast.error('Failed to load budgets')
    } finally {
      setLoading(false)
    }
  }

  const changeMonth = (delta) => {
    const [year, mon] = month.split('-').map(Number)
    let newMonth = mon + delta
    let newYear = year
    
    if (newMonth > 12) {
      newMonth = 1
      newYear++
    } else if (newMonth < 1) {
      newMonth = 12
      newYear--
    }
    
    setMonth(`${newYear}-${String(newMonth).padStart(2, '0')}`)
  }

  const openModal = (budget = null) => {
    if (budget) {
      setEditingBudget(budget)
      setFormData({
        category: budget.category,
        amount: budget.amount.toString()
      })
    } else {
      setEditingBudget(null)
      // Find a category without a budget
      const usedCategories = budgets.map(b => b.category)
      const availableCategory = CATEGORIES.find(c => !usedCategories.includes(c.value))
      setFormData({
        category: availableCategory?.value || 'Food',
        amount: ''
      })
    }
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingBudget(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      toast.error('Please enter a valid amount')
      return
    }

    setSubmitting(true)
    try {
      if (editingBudget) {
        await api.updateBudget(editingBudget.id, {
          amount: parseFloat(formData.amount)
        })
        toast.success('Budget updated')
      } else {
        await api.createBudget({
          category: formData.category,
          amount: parseFloat(formData.amount),
          month: month
        })
        toast.success('Budget created')
      }

      closeModal()
      fetchBudgets()
    } catch (error) {
      toast.error(error.message || 'Failed to save budget')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this budget?')) return

    try {
      await api.deleteBudget(id)
      toast.success('Budget deleted')
      fetchBudgets()
    } catch (error) {
      toast.error('Failed to delete budget')
    }
  }

  const getBudgetStatus = (budget) => {
    if (budget.percentage_used >= 100) return 'exceeded'
    if (budget.percentage_used >= 80) return 'warning'
    return 'ok'
  }

  const usedCategories = budgets.map(b => b.category)
  const availableCategories = CATEGORIES.filter(c => 
    !usedCategories.includes(c.value) || (editingBudget?.category === c.value)
  )

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-dark-100">Budgets</h1>
          <p className="text-dark-500 mt-1">Set spending limits for each category</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-dark-900/50 rounded-xl p-1">
            <button 
              onClick={() => changeMonth(-1)}
              className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-dark-400" />
            </button>
            <span className="px-4 py-2 font-medium text-dark-200 min-w-[140px] text-center">
              {getMonthName(month)}
            </span>
            <button 
              onClick={() => changeMonth(1)}
              className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-dark-400" />
            </button>
          </div>
          <button
            onClick={() => openModal()}
            className="btn-primary flex items-center gap-2"
            disabled={availableCategories.length === 0}
          >
            <Plus className="w-5 h-5" />
            Add Budget
          </button>
        </div>
      </div>

      {/* Summary Card */}
      <div className="glass-card p-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div>
            <p className="text-dark-500 text-sm mb-1">Total Budget</p>
            <p className="text-2xl font-bold text-dark-100">{formatCurrency(totalBudget)}</p>
          </div>
          <div>
            <p className="text-dark-500 text-sm mb-1">Total Spent</p>
            <p className="text-2xl font-bold text-dark-100">{formatCurrency(totalSpent)}</p>
          </div>
          <div>
            <p className="text-dark-500 text-sm mb-1">Remaining</p>
            <p className={`text-2xl font-bold ${
              totalBudget - totalSpent >= 0 ? 'text-success' : 'text-danger'
            }`}>
              {formatCurrency(Math.abs(totalBudget - totalSpent))}
              {totalBudget - totalSpent < 0 && ' over'}
            </p>
          </div>
        </div>
        <div className="mt-4">
          <div className="h-3 bg-dark-800 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                totalSpent > totalBudget ? 'bg-danger' : 
                totalSpent > totalBudget * 0.8 ? 'bg-warning' : 'bg-success'
              }`}
              style={{ width: `${Math.min((totalSpent / totalBudget) * 100 || 0, 100)}%` }}
            />
          </div>
          <p className="text-dark-500 text-sm mt-2 text-right">
            {totalBudget > 0 ? ((totalSpent / totalBudget) * 100).toFixed(0) : 0}% used
          </p>
        </div>
      </div>

      {/* Budgets Grid */}
      {loading ? (
        <div className="p-12 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : budgets.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <div className="w-16 h-16 rounded-full bg-dark-800 flex items-center justify-center mx-auto mb-4">
            <PiggyBank className="w-8 h-8 text-dark-500" />
          </div>
          <p className="text-dark-400 text-lg">No budgets set for {getMonthName(month)}</p>
          <p className="text-dark-600 mt-1">Create budgets to track your spending limits</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {budgets.map((budget) => {
            const catInfo = getCategoryInfo(budget.category)
            const status = getBudgetStatus(budget)
            
            return (
              <div key={budget.id} className="glass-card p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                      style={{ backgroundColor: `${catInfo.color}20` }}
                    >
                      {catInfo.icon}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-dark-100">
                        {budget.category}
                      </h3>
                      <span className={`inline-flex items-center gap-1 text-xs font-medium ${
                        status === 'exceeded' ? 'text-danger' :
                        status === 'warning' ? 'text-warning' : 'text-success'
                      }`}>
                        {status === 'exceeded' ? (
                          <><AlertTriangle className="w-3 h-3" /> Over budget</>
                        ) : status === 'warning' ? (
                          <><AlertTriangle className="w-3 h-3" /> Near limit</>
                        ) : (
                          <><CheckCircle className="w-3 h-3" /> On track</>
                        )}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => openModal(budget)}
                      className="p-2 text-dark-500 hover:text-primary-400 hover:bg-dark-800 rounded-lg transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(budget.id)}
                      className="p-2 text-dark-500 hover:text-danger hover:bg-dark-800 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-dark-500 text-sm">Spent</p>
                      <p className="text-xl font-bold text-dark-100">
                        {formatCurrency(budget.spent)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-dark-500 text-sm">Budget</p>
                      <p className="text-xl font-bold text-dark-400">
                        {formatCurrency(budget.amount)}
                      </p>
                    </div>
                  </div>

                  <div>
                    <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-500 ${
                          status === 'exceeded' ? 'bg-danger' :
                          status === 'warning' ? 'bg-warning' : 'bg-success'
                        }`}
                        style={{ 
                          width: `${Math.min(budget.percentage_used, 100)}%`,
                          backgroundColor: catInfo.color
                        }}
                      />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs text-dark-500">
                        {budget.percentage_used.toFixed(0)}% used
                      </span>
                      <span className={`text-xs font-medium ${
                        budget.remaining >= 0 ? 'text-success' : 'text-danger'
                      }`}>
                        {budget.remaining >= 0 ? formatCurrency(budget.remaining) + ' left' : formatCurrency(Math.abs(budget.remaining)) + ' over'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Add/Edit Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="glass-card w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-dark-100">
                {editingBudget ? 'Edit Budget' : 'Set Budget'}
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
                <label className="block text-sm text-dark-400 mb-2">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="input-field"
                  disabled={!!editingBudget}
                >
                  {(editingBudget ? CATEGORIES.filter(c => c.value === editingBudget.category) : availableCategories).map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.icon} {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-dark-400 mb-2">Budget Amount (₹)</label>
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

              <div className="bg-dark-800/50 rounded-lg p-4 text-sm text-dark-400">
                <p>This budget will apply to <strong className="text-dark-200">{getMonthName(month)}</strong></p>
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
                    editingBudget ? 'Update' : 'Set Budget'
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
function PiggyBank(props) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8 0 3 2 4.5V20h4v-2h3v2h4v-4c1-.5 1.7-1 2-2h2v-4h-2c0-1-.5-1.5-1-2V5z"/>
      <path d="M2 9v1c0 1.1.9 2 2 2h1"/>
      <path d="M16 11h.01"/>
    </svg>
  )
}
