export default function TransactionTable({ rows }: { rows: any[] }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-4">
      <h3 className="mb-4 text-sm text-slate-300">Live Transactions</h3>
      <div className="max-h-72 overflow-auto text-xs">
        <table className="w-full table-auto">
          <thead className="text-slate-400">
            <tr>
              <th className="text-left">User</th><th>Amount</th><th>Location</th><th>Risk</th><th>Score</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice().reverse().map((r, idx) => (
              <tr key={idx} className="border-t border-slate-800">
                <td>{r.user_id}</td><td className="text-center">${r.amount}</td><td className="text-center">{r.location}</td>
                <td className="text-center">{r.risk_level}</td><td className="text-center">{(r.fraud_probability || 0).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
