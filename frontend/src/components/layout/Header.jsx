import { Bell, Search, RefreshCw, Wifi, Home } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const navigate = useNavigate();

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1500);
    // Trigger a page-level data refresh via event
    window.dispatchEvent(new CustomEvent('refresh-data'));
  };

  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
  const dateStr = now.toLocaleDateString('en-IN', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });

  return (
    <header className="h-14 border-b border-white/[0.06] bg-[var(--bg-secondary)]/80 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-30">
      {/* Left: Home button, Title & market status */}
      <div className="flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/')}
          className="w-8 h-8 rounded-lg bg-[var(--bg-primary)] border border-white/[0.08] flex items-center justify-center hover:border-[var(--blue)]/50 transition-colors cursor-pointer shrink-0"
          title="Back to Home"
        >
          <Home size={14} className="text-[var(--text-secondary)]" />
        </motion.button>
        <div>
          <h2 className="text-sm font-semibold text-[var(--text-primary)] leading-none">
            Options Analytics Dashboard
          </h2>
          <p className="text-[11px] text-[var(--text-muted)] mt-0.5">
            Real-time derivatives market intelligence
          </p>
        </div>
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--green-dim)] border border-[var(--green)]/20">
          <Wifi size={10} className="text-[var(--green)]" />
          <span className="text-[10px] font-medium text-[var(--green)]">
            MARKET OPEN
          </span>
        </div>
      </div>

      {/* Right: Controls */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="hidden lg:flex items-center gap-2 bg-[var(--bg-primary)] border border-white/[0.08] rounded-lg px-3 py-1.5">
          <Search size={14} className="text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search strikes, symbols..."
            className="bg-transparent text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none w-48"
          />
        </div>

        {/* Time display */}
        <div className="hidden md:block text-right">
          <p className="text-xs font-mono font-medium text-[var(--text-primary)]">
            {timeStr}
          </p>
          <p className="text-[10px] text-[var(--text-muted)]">{dateStr}</p>
        </div>

        {/* Refresh button */}
        <motion.button
          onClick={handleRefresh}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="w-8 h-8 rounded-lg bg-[var(--bg-primary)] border border-white/[0.08] flex items-center justify-center hover:border-[var(--blue)]/50 transition-colors cursor-pointer"
        >
          <RefreshCw
            size={14}
            className={`text-[var(--text-secondary)] ${isRefreshing ? 'animate-spin' : ''}`}
          />
        </motion.button>

        {/* Notifications */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative w-8 h-8 rounded-lg bg-[var(--bg-primary)] border border-white/[0.08] flex items-center justify-center hover:border-[var(--blue)]/50 transition-colors cursor-pointer"
        >
          <Bell size={14} className="text-[var(--text-secondary)]" />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-[var(--red)] text-[8px] text-white flex items-center justify-center font-bold">
            3
          </span>
        </motion.button>
      </div>
    </header>
  );
}
