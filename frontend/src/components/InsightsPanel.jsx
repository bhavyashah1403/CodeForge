import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  Info,
} from 'lucide-react';

/**
 * InsightsPanel – Scrollable list of AI-generated smart alerts.
 *
 * Props:
 *  - insights: [{ type, title, description, timestamp, severity }, ...]
 */

const iconMap = {
  anomaly: <AlertTriangle size={16} />,
  bullish: <TrendingUp size={16} />,
  bearish: <TrendingDown size={16} />,
  volatility: <Activity size={16} />,
  spike: <Zap size={16} />,
  info: <Info size={16} />,
};

const colorMap = {
  anomaly: { bg: 'var(--yellow-dim)', border: 'var(--yellow)', text: 'var(--yellow)', icon: 'var(--yellow)' },
  bullish: { bg: 'var(--green-dim)', border: 'var(--green)', text: 'var(--green)', icon: 'var(--green)' },
  bearish: { bg: 'var(--red-dim)', border: 'var(--red)', text: 'var(--red)', icon: 'var(--red)' },
  volatility: { bg: 'var(--cyan-dim)', border: 'var(--cyan)', text: 'var(--cyan)', icon: 'var(--cyan)' },
  spike: { bg: 'var(--red-dim)', border: 'var(--red)', text: 'var(--red)', icon: 'var(--red)' },
  info: { bg: 'var(--blue-dim)', border: 'var(--blue)', text: 'var(--blue)', icon: 'var(--blue)' },
};

const severityBadge = {
  high: 'bg-[var(--red)] text-white',
  medium: 'bg-[var(--yellow)] text-black',
  low: 'bg-[var(--blue)] text-white',
};

export default function InsightsPanel({ insights = [] }) {
  return (
    <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
      <AnimatePresence>
        {insights.map((insight, i) => {
          const colors = colorMap[insight.type] || colorMap.info;
          const icon = iconMap[insight.type] || iconMap.info;

          return (
            <motion.div
              key={insight.id || i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="relative rounded-lg border overflow-hidden transition-all hover:scale-[1.01] cursor-default"
              style={{
                background: colors.bg,
                borderColor: colors.border,
                borderLeftWidth: '3px',
              }}
            >
              <div className="p-3.5">
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
                    style={{
                      background: `color-mix(in srgb, ${colors.icon} 20%, transparent)`,
                      color: colors.icon,
                    }}
                  >
                    {icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4
                        className="text-xs font-semibold uppercase tracking-wide"
                        style={{ color: colors.text }}
                      >
                        {insight.title}
                      </h4>
                      {insight.severity && (
                        <span
                          className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                            severityBadge[insight.severity] || severityBadge.low
                          }`}
                        >
                          {insight.severity}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                      {insight.description}
                    </p>
                    {insight.timestamp && (
                      <p className="text-[10px] text-[var(--text-muted)] mt-1.5 font-mono">
                        {insight.timestamp}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {insights.length === 0 && (
        <div className="text-center py-10 text-[var(--text-muted)]">
          <Activity size={32} className="mx-auto mb-2 opacity-30" />
          <p className="text-xs">No insights available</p>
        </div>
      )}
    </div>
  );
}
