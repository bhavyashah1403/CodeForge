import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
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
            {Number(entry.value).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function VolumeProfileChart({ data = [] }) {
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
          tickFormatter={(v) =>
            v >= 1e6
              ? (v / 1e6).toFixed(1) + 'M'
              : v >= 1e3
              ? (v / 1e3).toFixed(0) + 'K'
              : v
          }
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
          iconType="square"
          iconSize={10}
        />
        <Bar
          dataKey="volume_CE"
          name="Call Volume"
          fill="#ef4444"
          fillOpacity={0.7}
          radius={[3, 3, 0, 0]}
          stackId="volume"
        />
        <Bar
          dataKey="volume_PE"
          name="Put Volume"
          fill="#22c55e"
          fillOpacity={0.7}
          radius={[3, 3, 0, 0]}
          stackId="volume"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
