export default function AlertPanel({ alerts }: { alerts: any[] }) {
  return (
    <div className="rounded-xl border border-rose-700/60 bg-rose-950/20 p-4">
      <h3 className="mb-3 text-sm text-rose-300">Fraud Alerts</h3>
      <ul className="space-y-2 text-xs">
        {alerts.slice().reverse().slice(0, 8).map((a, idx) => (
          <li key={idx} className="rounded bg-slate-950/60 p-2">
            <span className="font-semibold text-rose-300">[{a.risk_level}]</span> {a.message}
          </li>
        ))}
      </ul>
    </div>
  )
}
