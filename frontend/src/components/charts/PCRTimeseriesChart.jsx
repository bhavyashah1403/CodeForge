import {
  LineChart,
  Line,
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
        {label}
      </p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-xs mb-1">
          <div
            className="w-2.5 h-2.5 rounded-full"
            style={{ background: entry.color }}
          />
          <span className="text-[var(--text-secondary)]">{entry.name}:</span>
          <span className="text-[var(--text-primary)] font-mono font-medium">
            {entry.name === 'Spot'
              ? Number(entry.value).toLocaleString()
              : Number(entry.value).toFixed(3)}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function PCRTimeseriesChart({ data = [] }) {
  const chartData = data.map((d) => ({
    ...d,
    time: d.datetime
      ? new Date(d.datetime).toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        })
      : d.time,
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="time"
          tick={{ fontSize: 9, fill: '#64748b' }}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
          interval="preserveStartEnd"
        />
        <YAxis
          yAxisId="pcr"
          tick={{ fontSize: 10, fill: '#64748b' }}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
          domain={['auto', 'auto']}
        />
        <YAxis
          yAxisId="spot"
          orientation="right"
          tick={{ fontSize: 10, fill: '#64748b' }}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
          domain={['auto', 'auto']}
          tickFormatter={(v) => (v / 1000).toFixed(1) + 'K'}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
          iconType="circle"
          iconSize={8}
        />
        <ReferenceLine
          yAxisId="pcr"
          y={1}
          stroke="rgba(255,255,255,0.15)"
          strokeDasharray="5 5"
          label={{
            value: 'Neutral',
            position: 'right',
            fontSize: 9,
            fill: '#64748b',
          }}
        />
        <Line
          yAxisId="pcr"
          type="monotone"
          dataKey="pcr_oi"
          name="PCR (OI)"
          stroke="#06b6d4"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 3 }}
        />
        <Line
          yAxisId="pcr"
          type="monotone"
          dataKey="pcr_volume"
          name="PCR (Vol)"
          stroke="#a855f7"
          strokeWidth={1.5}
          dot={false}
          strokeDasharray="5 2"
          activeDot={{ r: 3 }}
        />
        <Line
          yAxisId="spot"
          type="monotone"
          dataKey="spot"
          name="Spot"
          stroke="#f59e0b"
          strokeWidth={1.5}
          dot={false}
          activeDot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
