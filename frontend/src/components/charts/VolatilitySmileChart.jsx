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
  Legend,
} from 'recharts';

/**
 * VolatilitySmileChart – Shows Call IV & Put IV across strikes.
 *
 * Props:
 *  - data: [{ strike, iv_CE_pct, iv_PE_pct, iv }] (supports both formats)
 */

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[var(--bg-card)] border border-white/[0.1] rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-[var(--text-primary)] mb-2">
        Strike: {Number(label).toLocaleString()}
      </p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-xs mb-1">
          <div
            className="w-2.5 h-2.5 rounded-full"
            style={{ background: entry.color }}
          />
          <span className="text-[var(--text-secondary)]">{entry.name}:</span>
          <span className="text-[var(--text-primary)] font-mono font-medium">
            {Number(entry.value).toFixed(2)}%
          </span>
        </div>
      ))}
    </div>
  );
};

export default function VolatilitySmileChart({ data = [] }) {
  const hasMultiIV = data.length > 0 && (data[0].iv_CE_pct !== undefined || data[0].iv_CE !== undefined);

  const chartData = data.map((d) => ({
    ...d,
    iv_call: d.iv_CE_pct ?? d.iv_CE ?? d.iv ?? 0,
    iv_put: d.iv_PE_pct ?? d.iv_PE ?? d.iv ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart
        data={chartData}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        <defs>
          <linearGradient id="ivCEGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="ivPEGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="strike"
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) => (v / 1000).toFixed(1) + 'K'}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) => v.toFixed(1) + '%'}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
          domain={['auto', 'auto']}
        />
        <Tooltip content={<CustomTooltip />} />
        {hasMultiIV && (
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
            iconType="circle"
            iconSize={8}
          />
        )}
        <Area
          type="monotone"
          dataKey="iv_call"
          name="Call IV"
          stroke="#ef4444"
          strokeWidth={2}
          fill="url(#ivCEGrad)"
          dot={false}
          activeDot={{ r: 4, stroke: '#ef4444', strokeWidth: 2, fill: '#0b0f1a' }}
        />
        {hasMultiIV && (
          <Area
            type="monotone"
            dataKey="iv_put"
            name="Put IV"
            stroke="#22c55e"
            strokeWidth={2}
            fill="url(#ivPEGrad)"
            dot={false}
            activeDot={{ r: 4, stroke: '#22c55e', strokeWidth: 2, fill: '#0b0f1a' }}
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  );
}
