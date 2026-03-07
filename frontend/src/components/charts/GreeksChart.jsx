import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';

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
            className="w-2.5 h-2.5 rounded-sm"
            style={{ background: entry.color }}
          />
          <span className="text-[var(--text-secondary)]">{entry.name}:</span>
          <span className="text-[var(--text-primary)] font-mono font-medium">
            {Number(entry.value).toFixed(4)}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function GreeksChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart
        data={data}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
        barGap={1}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="strike"
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) => (v / 1000).toFixed(1) + 'K'}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#64748b' }}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
          iconType="square"
          iconSize={10}
        />
        <ReferenceLine y={0} stroke="rgba(255,255,255,0.1)" />
        <Bar
          dataKey="delta_CE"
          name="Call Delta"
          fill="#ef4444"
          fillOpacity={0.7}
          radius={[2, 2, 0, 0]}
        />
        <Bar
          dataKey="delta_PE"
          name="Put Delta"
          fill="#22c55e"
          fillOpacity={0.7}
          radius={[2, 2, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
