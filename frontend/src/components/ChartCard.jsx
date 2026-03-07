import { motion } from 'framer-motion';

/**
 * ChartCard – Wrapper for any chart with title & optional subtitle.
 *
 * Props:
 *  - title:    string
 *  - subtitle: string (optional)
 *  - children: chart content
 *  - delay:    animation delay
 *  - className: additional classes
 */
export default function ChartCard({
  title,
  subtitle,
  children,
  delay = 0,
  className = '',
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`chart-container ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            {title}
          </h3>
          {subtitle && (
            <p className="text-[11px] text-[var(--text-muted)] mt-0.5">
              {subtitle}
            </p>
          )}
        </div>
        {/* Live indicator dot */}
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-[var(--green)] animate-pulse" />
          <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider">
            Live
          </span>
        </div>
      </div>
      {children}
    </motion.div>
  );
}
