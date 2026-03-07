import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div className="bg-[var(--bg-card)] border border-white/[0.1] rounded-lg p-3 shadow-xl">
      <div className="space-y-1 text-xs">
        <p className="font-semibold text-[var(--text-primary)]">
          Strike: {Number(d?.strike).toLocaleString()}
        </p>
        <p className="text-[var(--text-secondary)]">
          Expiry: {d?.expiry?.split(' ')[0]}
        </p>
        {d?.iv_CE != null && (
          <div className="flex justify-between gap-3">
            <span className="text-[var(--text-secondary)]">Call IV:</span>
            <span className="font-mono text-[var(--red)]">{d.iv_CE}%</span>
          </div>
        )}
        {d?.iv_PE != null && (
          <div className="flex justify-between gap-3">
            <span className="text-[var(--text-secondary)]">Put IV:</span>
            <span className="font-mono text-[var(--green)]">{d.iv_PE}%</span>
          </div>
        )}
        {d?.time_to_expiry != null && (
          <div className="flex justify-between gap-3">
            <span className="text-[var(--text-secondary)]">Days to Exp:</span>
            <span className="font-mono text-[var(--text-primary)]">
              {d.time_to_expiry}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

const COLORS = ['#06b6d4', '#a855f7', '#f59e0b', '#22c55e', '#ef4444'];

export default function VolatilitySurfaceChart({ data = [] }) {
  // Group by expiry for different colored series
  const expiries = [...new Set(data.map((d) => d.expiry))];

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="strike"
          name="Strike"
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) => (v / 1000).toFixed(1) + 'K'}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <YAxis
          dataKey="iv_avg"
          name="IV %"
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) => v?.toFixed(1) + '%'}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
          domain={['auto', 'auto']}
        />
        <ZAxis
          dataKey="time_to_expiry"
          range={[30, 300]}
          name="Days to Expiry"
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
          iconType="circle"
          iconSize={8}
        />
        {expiries.map((exp, i) => (
          <Scatter
            key={exp}
            name={exp?.split(' ')[0] || `Expiry ${i + 1}`}
            data={data.filter((d) => d.expiry === exp)}
            fill={COLORS[i % COLORS.length]}
            fillOpacity={0.8}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}
