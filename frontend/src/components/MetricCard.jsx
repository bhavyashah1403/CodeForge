import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * MetricCard – Displays a single KPI with trend indicator.
 *
 * Props:
 *  - label:   string
 *  - value:   string | number
 *  - change:  number  (positive = up, negative = down, 0 = flat)
 *  - icon:    React node (Lucide icon)
 *  - color:   CSS variable name ('--green', '--red', '--blue', etc.)
 *  - delay:   animation stagger delay in seconds
 */
export default function MetricCard({
  label,
  value,
  change = 0,
  icon,
  color = '--blue',
  delay = 0,
}) {
  const isUp = change > 0;
  const isDown = change < 0;
  const trendColor = isUp ? 'var(--green)' : isDown ? 'var(--red)' : 'var(--text-muted)';
  const trendBg = isUp ? 'var(--green-dim)' : isDown ? 'var(--red-dim)' : 'rgba(100,116,139,0.1)';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="metric-card group"
    >
      {/* Top accent bar */}
      <div
        className="absolute top-0 left-0 right-0 h-[2px] rounded-t-xl opacity-60 group-hover:opacity-100 transition-opacity"
        style={{ background: `var(${color})` }}
      />

      <div className="flex items-start justify-between">
        {/* Icon */}
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
          style={{ background: `color-mix(in srgb, var(${color}) 15%, transparent)` }}
        >
          <span style={{ color: `var(${color})` }}>{icon}</span>
        </div>

        {/* Trend badge */}
        <div
          className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold"
          style={{ background: trendBg, color: trendColor }}
        >
          {isUp ? <TrendingUp size={12} /> : isDown ? <TrendingDown size={12} /> : <Minus size={12} />}
          {Math.abs(change).toFixed(2)}%
        </div>
      </div>

      {/* Value */}
      <div className="mt-3">
        <p className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-['JetBrains_Mono']">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        <p className="text-xs text-[var(--text-muted)] mt-1 uppercase tracking-wider">
          {label}
        </p>
      </div>
    </motion.div>
  );
}
