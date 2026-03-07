import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';

/**
 * CumulativeOIChart – Line chart showing OI change over time.
 *
 * Props:
 *  - data: [{ time, cumulative_oi_ce, cumulative_oi_pe }, ...]
 */

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[var(--bg-card)] border border-white/[0.1] rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-[var(--text-primary)] mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-xs mb-1">
          <div
            className="w-2.5 h-2.5 rounded-full"
            style={{ background: entry.color }}
          />
          <span className="text-[var(--text-secondary)]">{entry.name}:</span>
          <span className="text-[var(--text-primary)] font-mono font-medium">
            {Number(entry.value).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function CumulativeOIChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart
        data={data}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        <defs>
          <linearGradient id="ceOIGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="peOIGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="time"
          tick={{ fontSize: 10, fill: '#64748b' }}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) =>
            v >= 1000000
              ? (v / 1000000).toFixed(1) + 'M'
              : (v / 1000).toFixed(0) + 'K'
          }
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area
          type="monotone"
          dataKey="cumulative_oi_ce"
          name="Call OI"
          stroke="#ef4444"
          strokeWidth={2}
          fill="url(#ceOIGrad)"
          dot={false}
          activeDot={{ r: 4, stroke: '#ef4444', strokeWidth: 2, fill: '#0b0f1a' }}
        />
        <Area
          type="monotone"
          dataKey="cumulative_oi_pe"
          name="Put OI"
          stroke="#22c55e"
          strokeWidth={2}
          fill="url(#peOIGrad)"
          dot={false}
          activeDot={{ r: 4, stroke: '#22c55e', strokeWidth: 2, fill: '#0b0f1a' }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
