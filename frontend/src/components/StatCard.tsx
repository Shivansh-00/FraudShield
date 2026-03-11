import { motion } from 'framer-motion'

export default function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 shadow-lg">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-cyan-300">{value}</p>
    </motion.div>
  )
}
