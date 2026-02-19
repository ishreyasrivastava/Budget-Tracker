import { Link } from 'react-router-dom'
import { 
  PiggyBank, 
  ArrowRight,
  BarChart3,
  Brain,
  ShieldAlert,
} from 'lucide-react'

const features = [
  {
    icon: BarChart3,
    title: 'Expense Tracking',
    description: 'Add and categorize your daily expenses. Filter by date or category to see where your money goes.',
  },
  {
    icon: Brain,
    title: 'Spending Predictions',
    description: 'Uses basic ML to estimate next month\'s spending based on your past data.',
  },
  {
    icon: ShieldAlert,
    title: 'Anomaly Detection',
    description: 'Flags expenses that look unusual compared to your normal spending patterns.',
  },
  {
    icon: PiggyBank,
    title: 'Budget Limits',
    description: 'Set monthly budgets for each category and get alerts when you\'re close to the limit.',
  },
]

export default function Home() {
  return (
    <div className="min-h-screen bg-dark-950">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-950 border-b border-dark-800/50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center">
              <PiggyBank className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-dark-100">BudgetWise</span>
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
          <h1 className="text-4xl sm:text-5xl font-bold text-dark-100 leading-tight mb-6">
            Track your spending
          </h1>
          <p className="text-lg text-dark-400 max-w-2xl mx-auto mb-10">
            A simple expense tracker with budget limits, spending predictions, and anomaly detection. Built as a college project.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="btn-primary px-8 py-3 text-lg flex items-center gap-2">
              Sign Up <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/login" className="btn-secondary px-8 py-3 text-lg">
              Log In
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-dark-100 mb-4">
              What it does
            </h2>
            <p className="text-dark-400 text-lg max-w-2xl mx-auto">
              Core features to help you keep track of your money.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {features.map((f) => {
              const Icon = f.icon
              return (
                <div key={f.title} className="bg-dark-900 border border-dark-800 rounded-xl p-6">
                  <div className="w-12 h-12 rounded-xl bg-primary-600/20 flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-primary-400" />
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
        <div className="max-w-3xl mx-auto text-center bg-dark-900 border border-dark-800 rounded-xl p-12">
          <h2 className="text-3xl font-bold text-dark-100 mb-4">Want to try it out?</h2>
          <p className="text-dark-400 mb-8">Create an account and start tracking your expenses.</p>
          <Link to="/signup" className="btn-primary px-8 py-3 text-lg inline-flex items-center gap-2">
            Get Started <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-800/50 py-8 px-4 text-center text-dark-600 text-sm">
        © 2025 BudgetWise
      </footer>
    </div>
  )
}
