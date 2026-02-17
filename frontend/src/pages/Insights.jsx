/**
 * AI Insights page — predictions, anomalies, and smart insights.
 */

import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { formatCurrency } from '../lib/constants'
import {
  Brain,
  TrendingUp,
  TrendingDown,
  ShieldAlert,
  Lightbulb,
  Loader2,
  AlertTriangle,
  Info
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts'
import toast from 'react-hot-toast'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8', '#4f46e5']

const severityColors = {
  high: 'bg-red-500/20 text-red-400 border-red-500/30',
  medium: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  low: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
}

export default function Insights() {
  const [predictions, setPredictions] = useState(null)
  const [anomalies, setAnomalies] = useState(null)
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    setLoading(true)
    try {
      const [pred, anom, ins] = await Promise.allSettled([
        api.getAIPredictions(),
        api.getAIAnomalies(),
        api.getAIInsights(),
      ])
      if (pred.status === 'fulfilled') setPredictions(pred.value)
      if (anom.status === 'fulfilled') setAnomalies(anom.value)
      if (ins.status === 'fulfilled') setInsights(ins.value)
    } catch (e) {
      toast.error('Failed to load AI insights')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    )
  }

  const predictionData = predictions?.predictions || predictions?.categories || []
  const anomalyData = anomalies?.anomalies || []
  const insightData = insights?.insights || []

  // Normalize prediction data for chart
  const chartData = Array.isArray(predictionData)
    ? predictionData.map((p) => ({
        category: p.category,
        predicted: p.predicted_amount || p.amount || 0,
        trend: p.trend || 'stable',
      }))
    : []

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold text-dark-100">AI Insights</h1>
        </div>
        <p className="text-dark-500">Machine learning-powered analysis of your spending patterns</p>
      </div>

      {/* Predictions */}
      <section>
        <h2 className="text-xl font-semibold text-dark-100 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-400" />
          Next Month Predictions
        </h2>
        {chartData.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart */}
            <div className="glass-card p-6">
              <h3 className="text-sm text-dark-500 mb-4">Predicted Spend by Category</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis
                      dataKey="category"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#64748b', fontSize: 12 }}
                      angle={-30}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#64748b', fontSize: 12 }}
                      tickFormatter={(v) => `₹${v}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #334155',
                        borderRadius: '8px',
                      }}
                      formatter={(v) => [formatCurrency(v), 'Predicted']}
                    />
                    <Bar dataKey="predicted" radius={[6, 6, 0, 0]}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Cards */}
            <div className="space-y-3">
              {chartData.map((p) => (
                <div key={p.category} className="glass-card p-4 flex items-center justify-between">
                  <div>
                    <p className="text-dark-100 font-medium">{p.category}</p>
                    <p className="text-dark-500 text-sm">Predicted spend</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-dark-100">
                      {formatCurrency(p.predicted)}
                    </span>
                    {p.trend === 'up' ? (
                      <TrendingUp className="w-5 h-5 text-red-400" />
                    ) : p.trend === 'down' ? (
                      <TrendingDown className="w-5 h-5 text-green-400" />
                    ) : (
                      <span className="text-dark-500 text-sm">—</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <EmptyState icon={TrendingUp} message="No predictions available yet. Add more expenses to enable AI predictions." />
        )}
      </section>

      {/* Anomalies */}
      <section>
        <h2 className="text-xl font-semibold text-dark-100 mb-4 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-orange-400" />
          Anomaly Detection
        </h2>
        {anomalyData.length > 0 ? (
          <div className="space-y-3">
            {anomalyData.map((a, i) => {
              const severity = a.severity || 'medium'
              return (
                <div key={i} className="glass-card p-4 flex items-start gap-4">
                  <AlertTriangle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                    severity === 'high' ? 'text-red-400' : severity === 'medium' ? 'text-orange-400' : 'text-yellow-400'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-dark-100 font-medium">
                        {a.description || a.message || `Unusual expense in ${a.category}`}
                      </p>
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${severityColors[severity]}`}>
                        {severity}
                      </span>
                    </div>
                    <p className="text-dark-500 text-sm">
                      {a.category && `Category: ${a.category}`}
                      {a.amount && ` • Amount: ${formatCurrency(a.amount)}`}
                      {a.expected_range && ` • Expected: ${a.expected_range}`}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <EmptyState icon={ShieldAlert} message="No anomalies detected. Your spending patterns look normal!" />
        )}
      </section>

      {/* Smart Insights */}
      <section>
        <h2 className="text-xl font-semibold text-dark-100 mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          Smart Insights
        </h2>
        {insightData.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {insightData.map((insight, i) => (
              <div key={i} className="glass-card p-5">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-dark-100 font-medium mb-1">{insight.title || insight.type || 'Insight'}</p>
                    <p className="text-dark-400 text-sm leading-relaxed">{insight.message || insight.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState icon={Lightbulb} message="No insights available yet. Keep tracking expenses to unlock AI-powered insights." />
        )}
      </section>
    </div>
  )
}

function EmptyState({ icon: Icon, message }) {
  return (
    <div className="glass-card p-8 text-center">
      <Icon className="w-10 h-10 text-dark-600 mx-auto mb-3" />
      <p className="text-dark-500">{message}</p>
    </div>
  )
}
