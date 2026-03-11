import { useCallback, useEffect, useMemo, useState } from 'react'
import AlertPanel from '../components/AlertPanel'
import FraudTrendChart from '../components/FraudTrendChart'
import RiskHistogram from '../components/RiskHistogram'
import StatCard from '../components/StatCard'
import TransactionTable from '../components/TransactionTable'
import { useLiveFeed } from '../hooks/useLiveFeed'
import { fetchAlerts, fetchStats, fetchTransactions } from '../services/api'

export default function App() {
  const [stats, setStats] = useState<any>({})
  const [transactions, setTransactions] = useState<any[]>([])
  const [alerts, setAlerts] = useState<any[]>([])
  const [liveStatus, setLiveStatus] = useState('connected')

  const refresh = useCallback(async () => {
    setStats(await fetchStats())
    setTransactions(await fetchTransactions())
    setAlerts(await fetchAlerts())
  }, [])

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, 8000)
    return () => clearInterval(timer)
  }, [refresh])

  useLiveFeed((payload) => {
    setLiveStatus('connected')
    if (payload.event === 'transaction') setTransactions((prev) => [...prev, payload.data])
    if (payload.event === 'alert') setAlerts((prev) => [...prev, payload.data])
  })

  const trendData = useMemo(
    () =>
      transactions.slice(-20).map((t, i) => ({
        time: `${i + 1}`,
        fraud: t.risk_level === 'High' || t.risk_level === 'Critical' ? 1 : 0
      })),
    [transactions]
  )

  return (
    <main className="min-h-screen p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-cyan-300">FraudShield AI – Real-Time Fraud Command Center</h1>
            <p className="text-slate-400">Explainable fraud intelligence for digital payments at banking scale.</p>
          </div>
          <span className="rounded-full border border-emerald-600 bg-emerald-950/50 px-3 py-1 text-xs text-emerald-300">
            Live stream: {liveStatus}
          </span>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          <StatCard label="Total Transactions" value={stats.total_transactions ?? 0} />
          <StatCard label="Fraud Transactions" value={stats.fraud_transactions ?? 0} />
          <StatCard label="Fraud %" value={`${stats.fraud_percentage ?? 0}%`} />
          <StatCard label="Suspicious Accounts" value={stats.suspicious_accounts ?? 0} />
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2"><FraudTrendChart data={trendData} /></div>
          <AlertPanel alerts={alerts} />
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2"><TransactionTable rows={transactions} /></div>
          <RiskHistogram rows={transactions} />
        </section>
      </div>
    </main>
  )
}
