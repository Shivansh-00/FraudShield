import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function RiskHistogram({ rows }: { rows: any[] }) {
  const buckets = [
    { name: 'Low', count: 0 },
    { name: 'Medium', count: 0 },
    { name: 'High', count: 0 },
    { name: 'Critical', count: 0 }
  ]

  rows.forEach((row) => {
    const index = buckets.findIndex((b) => b.name === row.risk_level)
    if (index >= 0) buckets[index].count += 1
  })

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-4">
      <h3 className="mb-4 text-sm text-slate-300">Risk Score Distribution</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={buckets}>
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="count" fill="#06b6d4" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
