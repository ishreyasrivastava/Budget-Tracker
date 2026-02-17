/**
 * Landing/Home page with hero, features, and stats.
 */

import { Link } from 'react-router-dom'
import { 
  TrendingUp, 
  Brain, 
  ShieldAlert, 
  PiggyBank, 
  ArrowRight,
  BarChart3,
  Zap,
  Users
} from 'lucide-react'

const features = [
  {
    icon: BarChart3,
    title: 'Expense Tracking',
    description: 'Track every rupee with categorized expenses, filters, and detailed breakdowns.',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Brain,
    title: 'AI Predictions',
    description: 'Machine learning models predict your next month spending per category.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: ShieldAlert,
    title: 'Anomaly Detection',
    description: 'Automatically flags unusual expenses so you never miss suspicious activity.',
    color: 'from-orange-500 to-red-500',
  },
  {
    icon: PiggyBank,
    title: 'Budget Management',
    description: 'Set monthly budgets per category with real-time alerts when you\'re close to limits.',
    color: 'from-green-500 to-emerald-500',
  },
]

const stats = [
  { value: '10K+', label: 'Expenses Tracked' },
  { value: '₹2.4Cr', label: 'Money Managed' },
  { value: '95%', label: 'Prediction Accuracy' },
  { value: '500+', label: 'Happy Users' },
]

export default function Home() {
  return (
    <div className="min-h-screen bg-dark-950">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-950/80 backdrop-blur-xl border-b border-dark-800/50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <PiggyBank className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">BudgetPro</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary text-sm">Log In</Link>
            <Link to="/signup" className="btn-primary text-sm flex items-center gap-1">
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-600/10 border border-primary-500/20 text-primary-400 text-sm font-medium mb-8">
            <Zap className="w-4 h-4" />
            Powered by AI
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-dark-100 leading-tight mb-6">
            Smart Budget Tracking{' '}
            <span className="gradient-text">with AI</span>
          </h1>
          <p className="text-lg sm:text-xl text-dark-400 max-w-2xl mx-auto mb-10">
            Track expenses, predict future spending, detect anomalies, and get intelligent insights — all in one beautiful dashboard.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="btn-primary px-8 py-3 text-lg flex items-center gap-2">
              Start Free <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/login" className="btn-secondary px-8 py-3 text-lg">
              Log In
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-4 border-y border-dark-800/50">
        <div className="max-w-5xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-8">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-3xl font-bold gradient-text">{stat.value}</p>
              <p className="text-dark-500 text-sm mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-dark-100 mb-4">
              Everything you need to{' '}
              <span className="gradient-text">master your finances</span>
            </h2>
            <p className="text-dark-400 text-lg max-w-2xl mx-auto">
              From simple expense tracking to AI-powered predictions, we've got you covered.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {features.map((f) => {
              const Icon = f.icon
              return (
                <div key={f.title} className="glass-card p-6 hover:border-primary-500/30 transition-all duration-300 group">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-dark-100 mb-2">{f.title}</h3>
                  <p className="text-dark-400 leading-relaxed">{f.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto text-center glass-card p-12">
          <h2 className="text-3xl font-bold text-dark-100 mb-4">Ready to take control?</h2>
          <p className="text-dark-400 mb-8">Join thousands of users who manage their finances smarter with AI.</p>
          <Link to="/signup" className="btn-primary px-8 py-3 text-lg inline-flex items-center gap-2">
            Get Started Free <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-800/50 py-8 px-4 text-center text-dark-600 text-sm">
        © 2026 BudgetPro. Built with ❤️ and AI.
      </footer>
    </div>
  )
}
