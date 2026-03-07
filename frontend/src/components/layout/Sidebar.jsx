import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  BarChart3,
  Calendar,
  SlidersHorizontal,
  Clock,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import { fetchExpiries } from '../../services/api';

// Only NIFTY data is available in the training dataset
const assets = ['NIFTY'];

const fallbackExpiries = ['2026-02-17', '2026-02-24', '2026-03-02'];

export default function Sidebar({ filters, onFilterChange }) {
  const [collapsed, setCollapsed] = useState(false);
  const [expiryDates, setExpiryDates] = useState(fallbackExpiries);

  useEffect(() => {
    fetchExpiries()
      .then((res) => {
        const list = res?.expiries || res;
        if (Array.isArray(list) && list.length > 0) setExpiryDates(list);
      })
      .catch(() => {});
  }, []);

  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value });
  };

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 64 : 280 }}
      className="sidebar-transition h-screen sticky top-0 flex flex-col border-r border-white/[0.06] bg-[var(--bg-secondary)] z-40"
    >
      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-[var(--blue)] flex items-center justify-center shadow-lg hover:scale-110 transition-transform z-50 cursor-pointer"
      >
        {collapsed ? (
          <ChevronRight size={14} className="text-white" />
        ) : (
          <ChevronLeft size={14} className="text-white" />
        )}
      </button>

      {/* Logo area */}
      <div className="p-4 border-b border-white/[0.06] flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center shrink-0">
          <TrendingUp size={18} className="text-white" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              <h1 className="text-sm font-bold text-[var(--text-primary)] leading-tight">
                CodeForge
              </h1>
              <p className="text-[10px] text-[var(--text-muted)] tracking-wider uppercase">
                Options Analytics
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Filters — hidden when collapsed */}
      <AnimatePresence>
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex-1 overflow-y-auto p-4 space-y-5"
          >
            {/* Asset selector */}
            <FilterGroup icon={<BarChart3 size={14} />} label="Asset">
              <select
                value={filters.asset}
                onChange={(e) => handleChange('asset', e.target.value)}
                className="w-full bg-[var(--bg-primary)] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--blue)] transition-colors cursor-pointer"
              >
                {assets.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
            </FilterGroup>

            {/* Expiry date */}
            <FilterGroup icon={<Calendar size={14} />} label="Expiry Date">
              <select
                value={filters.expiry}
                onChange={(e) => handleChange('expiry', e.target.value)}
                className="w-full bg-[var(--bg-primary)] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--blue)] transition-colors cursor-pointer"
              >
                {expiryDates.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </FilterGroup>

            {/* Strike range */}
            <FilterGroup icon={<SlidersHorizontal size={14} />} label={`Strike Range: ${filters.strikeRange.toLocaleString()}`}>
              <input
                type="range"
                min={20000}
                max={30000}
                step={100}
                value={filters.strikeRange}
                onChange={(e) => handleChange('strikeRange', Number(e.target.value))}
                className="w-full mt-1"
              />
              <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-1">
                <span>20,000</span>
                <span>30,000</span>
              </div>
            </FilterGroup>

            {/* Time range */}
            <FilterGroup icon={<Clock size={14} />} label={`Time Window: ${filters.timeRange}h`}>
              <input
                type="range"
                min={1}
                max={24}
                step={1}
                value={filters.timeRange}
                onChange={(e) => handleChange('timeRange', Number(e.target.value))}
                className="w-full mt-1"
              />
              <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-1">
                <span>1h</span>
                <span>24h</span>
              </div>
            </FilterGroup>

            {/* AI Anomalies toggle */}
            <FilterGroup icon={<Sparkles size={14} />} label="AI Anomalies">
              <div className="flex items-center gap-3 mt-1">
                <div
                  onClick={() => handleChange('showAnomalies', !filters.showAnomalies)}
                  className={`toggle-switch ${filters.showAnomalies ? 'active' : ''}`}
                />
                <span className="text-xs text-[var(--text-secondary)]">
                  {filters.showAnomalies ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </FilterGroup>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <AnimatePresence>
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="p-4 border-t border-white/[0.06]"
          >
            <div className="flex items-center gap-2">
              <div className="pulse-dot bg-[var(--green)]" />
              <span className="text-[11px] text-[var(--text-muted)]">
                Live Data Connected
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.aside>
  );
}

function FilterGroup({ icon, label, children }) {
  return (
    <div>
      <label className="flex items-center gap-2 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider mb-2">
        <span className="text-[var(--blue)]">{icon}</span>
        {label}
      </label>
      {children}
    </div>
  );
}
