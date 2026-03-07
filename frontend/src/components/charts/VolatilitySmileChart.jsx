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
 * VolatilitySmileChart – Line chart of Strike vs Implied Volatility.
 *
 * Props:
 *  - data: [{ strike, iv }, ...]
 */

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[var(--bg-card)] border border-white/[0.1] rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-[var(--text-primary)] mb-1">
        Strike: {Number(label).toLocaleString()}
      </p>
      <div className="flex items-center gap-2 text-xs">
        <div className="w-2.5 h-2.5 rounded-full bg-[var(--cyan)]" />
        <span className="text-[var(--text-secondary)]">IV:</span>
        <span className="text-[var(--text-primary)] font-mono font-medium">
          {Number(payload[0].value).toFixed(2)}%
        </span>
      </div>
    </div>
  );
};

export default function VolatilitySmileChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart
        data={data}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        <defs>
          <linearGradient id="ivGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
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
        <Area
          type="monotone"
          dataKey="iv"
          stroke="#06b6d4"
          strokeWidth={2.5}
          fill="url(#ivGradient)"
          dot={false}
          activeDot={{
            r: 5,
            stroke: '#06b6d4',
            strokeWidth: 2,
            fill: '#0b0f1a',
          }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
