/**
 * Dashboard page with spending overview and analytics.
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { 
  formatCurrency, 
  getCurrentMonth, 
  getMonthName, 
  getCategoryInfo,
  formatDate 
} from '../lib/constants'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Wallet,
  PiggyBank,
  ArrowRight,
  Loader2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip 
} from 'recharts'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [month, setMonth] = useState(getCurrentMonth())

  useEffect(() => {
    fetchDashboard()
  }, [month])

  const fetchDashboard = async () => {
    setLoading(true)
    try {
      const [dashboardData, alertsData] = await Promise.all([
        api.getDashboard(month),
        api.getAlerts()
      ])
      setData(dashboardData)
      setAlerts(alertsData.alerts || [])
    } catch (error) {
      toast.error('Failed to load dashboard')
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    )
  }

  const budgetPercentage = data?.total_budget_this_month > 0 
    ? (data.total_spent_this_month / data.total_budget_this_month * 100) 
    : 0

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header with Month Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-dark-100">Dashboard</h1>
          <p className="text-dark-500 mt-1">Your financial overview</p>
        </div>
        <div className="flex items-center gap-2 bg-dark-900/50 rounded-xl p-1">
          <button 
            onClick={() => changeMonth(-1)}
            className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-dark-400" />
          </button>
          <span className="px-4 py-2 font-medium text-dark-200 min-w-[160px] text-center">
            {getMonthName(month)}
          </span>
          <button 
            onClick={() => changeMonth(1)}
            className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-dark-400" />
          </button>
        </div>
      </div>

      {/* Budget Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-3">
          {alerts.map((alert, idx) => (
            <div 
              key={idx}
              className={`glass-card p-4 flex items-center gap-4 border-l-4 ${
                alert.type === 'exceeded' ? 'border-l-danger' : 'border-l-warning'
              }`}
            >
              <AlertTriangle className={`w-5 h-5 flex-shrink-0 ${
                alert.type === 'exceeded' ? 'text-danger' : 'text-warning'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-dark-100 font-medium">{alert.message}</p>
                <p className="text-dark-500 text-sm">
                  {formatCurrency(alert.spent)} of {formatCurrency(alert.budget)} ({alert.percentage}%)
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-primary-600/20 flex items-center justify-center">
              <Wallet className="w-5 h-5 text-primary-400" />
            </div>
            <span className="text-dark-500 text-sm">Total Spent</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {formatCurrency(data?.total_spent_this_month || 0)}
          </p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-success/20 flex items-center justify-center">
              <PiggyBank className="w-5 h-5 text-success" />
            </div>
            <span className="text-dark-500 text-sm">Total Budget</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {formatCurrency(data?.total_budget_this_month || 0)}
          </p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              data?.remaining_budget >= 0 ? 'bg-success/20' : 'bg-danger/20'
            }`}>
              {data?.remaining_budget >= 0 ? (
                <TrendingUp className="w-5 h-5 text-success" />
              ) : (
                <TrendingDown className="w-5 h-5 text-danger" />
              )}
            </div>
            <span className="text-dark-500 text-sm">Remaining</span>
          </div>
          <p className={`text-2xl font-bold ${
            data?.remaining_budget >= 0 ? 'text-success' : 'text-danger'
          }`}>
            {formatCurrency(Math.abs(data?.remaining_budget || 0))}
            {data?.remaining_budget < 0 && ' over'}
          </p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              budgetPercentage > 100 ? 'bg-danger/20' : 
              budgetPercentage > 80 ? 'bg-warning/20' : 'bg-success/20'
            }`}>
              <span className={`text-sm font-bold ${
                budgetPercentage > 100 ? 'text-danger' : 
                budgetPercentage > 80 ? 'text-warning' : 'text-success'
              }`}>
                %
              </span>
            </div>
            <span className="text-dark-500 text-sm">Budget Used</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {budgetPercentage.toFixed(0)}%
          </p>
          <div className="mt-2 h-2 bg-dark-800 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                budgetPercentage > 100 ? 'bg-danger' : 
                budgetPercentage > 80 ? 'bg-warning' : 'bg-success'
              }`}
              style={{ width: `${Math.min(budgetPercentage, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-dark-100 mb-4">Spending by Category</h3>
          {data?.category_breakdown?.length > 0 ? (
            <div className="flex flex-col lg:flex-row items-center gap-6">
              <div className="w-48 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.category_breakdown}
                      dataKey="amount"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                    >
                      {data.category_breakdown.map((entry, index) => (
                        <Cell key={index} fill={getCategoryInfo(entry.category).color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 space-y-3">
                {data.category_breakdown.slice(0, 5).map((cat, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <span className="text-xl">{getCategoryInfo(cat.category).icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-dark-200 text-sm">{cat.category}</span>
                        <span className="text-dark-100 font-medium text-sm">
                          {formatCurrency(cat.amount)}
                        </span>
                      </div>
                      <div className="mt-1 h-1.5 bg-dark-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full"
                          style={{ 
                            width: `${cat.percentage}%`,
                            backgroundColor: getCategoryInfo(cat.category).color
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-dark-500">
              No expenses this month
            </div>
          )}
        </div>

        {/* Spending Trend */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-dark-100 mb-4">Daily Spending</h3>
          {data?.spending_trend?.length > 0 ? (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.spending_trend}>
                  <defs>
                    <linearGradient id="colorSpending" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="date" 
                    axisLine={false} 
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    tickFormatter={(val) => new Date(val).getDate()}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    tickFormatter={(val) => `₹${val}`}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }}
                    labelFormatter={(val) => formatDate(val)}
                    formatter={(val) => [formatCurrency(val), 'Spent']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="amount" 
                    stroke="#6366f1" 
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorSpending)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-dark-500">
              No data available
            </div>
          )}
        </div>
      </div>

      {/* Recent Expenses */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-dark-100">Recent Expenses</h3>
          <Link 
            to="/expenses"
            className="text-primary-400 hover:text-primary-300 text-sm font-medium flex items-center gap-1"
          >
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        {data?.recent_expenses?.length > 0 ? (
          <div className="space-y-3">
            {data.recent_expenses.map((expense) => {
              const catInfo = getCategoryInfo(expense.category)
              return (
                <div 
                  key={expense.id}
                  className="flex items-center gap-4 p-3 rounded-xl bg-dark-800/30 hover:bg-dark-800/50 transition-colors"
                >
                  <div 
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                    style={{ backgroundColor: `${catInfo.color}20` }}
                  >
                    {catInfo.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-dark-100 font-medium truncate">
                      {expense.description || expense.category}
                    </p>
                    <p className="text-dark-500 text-sm">{formatDate(expense.date)}</p>
                  </div>
                  <span className="text-dark-100 font-semibold">
                    {formatCurrency(expense.amount)}
                  </span>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="py-8 text-center text-dark-500">
            No expenses yet. Start tracking your spending!
          </div>
        )}
      </div>
    </div>
  )
}
