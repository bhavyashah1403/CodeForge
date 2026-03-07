import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  BarChart3,
  Activity,
  Sparkles,
  PieChart,
  Target,
  TrendingUp,
  TrendingDown,
  Zap,
  Shield,
  Eye,
  Layers,
  ArrowRight,
  ChevronRight,
  Play,
  Github,
  ExternalLink,
  Database,
  BrainCircuit,
  LineChart,
  Flame,
  Search,
  Clock,
  Code2,
} from 'lucide-react';

/* ── Animation variants ─────────────────────────────────────── */
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.12, ease: [0.25, 0.46, 0.45, 0.94] },
  }),
};

const stagger = {
  visible: { transition: { staggerChildren: 0.1 } },
};

/* ── Data ────────────────────────────────────────────────────── */
const features = [
  {
    icon: <BarChart3 size={24} />,
    title: 'Options Market Visualization',
    desc: 'Interactive charts that reveal Open Interest walls, support/resistance zones, and trading activity across strikes.',
    color: '--cyan',
  },
  {
    icon: <Activity size={24} />,
    title: 'Volatility Intelligence',
    desc: 'Analyze volatility smile and skew patterns to detect potential mispricing in the options market.',
    color: '--blue',
  },
  {
    icon: <Sparkles size={24} />,
    title: 'AI-Powered Anomaly Detection',
    desc: 'Machine learning models automatically detect unusual spikes in volume or volatility indicating institutional activity.',
    color: '--yellow',
  },
  {
    icon: <PieChart size={24} />,
    title: 'Market Sentiment Indicators',
    desc: 'Real-time calculation of Put-Call Ratio and structural signals to help traders understand market direction.',
    color: '--green',
  },
];

const useCases = [
  {
    icon: <Target size={20} />,
    text: 'Detect support and resistance levels from Open Interest concentration',
  },
  {
    icon: <Eye size={20} />,
    text: 'Identify unusual institutional activity in options markets',
  },
  {
    icon: <TrendingUp size={20} />,
    text: 'Monitor volatility changes before major price movements',
  },
  {
    icon: <BrainCircuit size={20} />,
    text: 'Assist quantitative research and options strategy development',
  },
  {
    icon: <Shield size={20} />,
    text: 'Risk management through real-time Greeks and exposure tracking',
  },
  {
    icon: <Clock size={20} />,
    text: 'Time-series analytics for intraday pattern recognition',
  },
];

const innovations = [
  {
    icon: <Zap size={20} />,
    title: 'AI-Driven Detection',
    desc: 'Unusual options activity spotted automatically by trained ML models.',
  },
  {
    icon: <Flame size={20} />,
    title: 'Interactive Heatmaps',
    desc: 'Time vs Strike heatmaps for intraday volume and OI analysis.',
  },
  {
    icon: <LineChart size={20} />,
    title: 'Volatility Structure',
    desc: 'Cross-strike and cross-expiry volatility surface analytics.',
  },
  {
    icon: <Layers size={20} />,
    title: 'Real-Time Dashboard',
    desc: 'Live analytics dashboard with streaming market insights.',
  },
];

const techStack = [
  { name: 'React', color: '#61DAFB' },
  { name: 'TailwindCSS', color: '#38BDF8' },
  { name: 'Plotly.js', color: '#3F4F75' },
  { name: 'Recharts', color: '#8884d8' },
  { name: 'Python', color: '#3776AB' },
  { name: 'Pandas', color: '#150458' },
  { name: 'Scikit-learn', color: '#F7931E' },
  { name: 'DuckDB', color: '#FFF000' },
  { name: 'Streamlit', color: '#FF4B4B' },
  { name: 'NumPy', color: '#013243' },
];

const stats = [
  { label: 'Data Points Analyzed', value: '14M+' },
  { label: 'Strikes Tracked', value: '300+' },
  { label: 'AI Models Used', value: '5' },
  { label: 'FOSS Technologies', value: '10+' },
];

/* ── Page Component ──────────────────────────────────────────── */
export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] overflow-x-hidden">
      {/* ━━ NAVBAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/[0.06] bg-[var(--bg-primary)]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center">
              <TrendingUp size={18} className="text-white" />
            </div>
            <div>
              <span className="text-sm font-bold tracking-tight">CodeForge</span>
              <span className="text-[10px] text-[var(--text-muted)] block -mt-0.5 uppercase tracking-widest">
                Options Analytics
              </span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              Features
            </a>
            <a href="#use-cases" className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              Use Cases
            </a>
            <a href="#innovation" className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              Innovation
            </a>
            <a href="#tech" className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              Tech Stack
            </a>
          </div>

          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-cyan-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 transition-shadow cursor-pointer"
          >
            Open Dashboard
            <ArrowRight size={14} />
          </motion.button>
        </div>
      </nav>

      {/* ━━ HERO SECTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <section className="relative pt-32 pb-20 px-6 min-h-[95vh] flex flex-col justify-center">
        {/* ── Fullscreen Background Video ── */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <video
            className="absolute inset-0 w-full h-full object-cover"
            autoPlay
            muted
            loop
            playsInline
          >
            <source
              src="https://res.cloudinary.com/dn4htye6b/video/upload/v1772867504/14683955_3840_2160_30fps_xn8vwi.mp4"
              type="video/mp4"
            />
          </video>

          {/* Heavy dark overlay layers for readability */}
          <div className="absolute inset-0 bg-[var(--bg-primary)]/80" />
          <div className="absolute inset-0 bg-gradient-to-b from-[var(--bg-primary)] via-transparent to-[var(--bg-primary)]" />
          <div className="absolute inset-0 bg-gradient-to-r from-[var(--bg-primary)]/90 via-[var(--bg-primary)]/50 to-[var(--bg-primary)]/70" />

          {/* Color accent glows */}
          <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-indigo-600/[0.1] rounded-full blur-[120px]" />
          <div className="absolute top-40 right-1/4 w-[400px] h-[400px] bg-cyan-500/[0.08] rounded-full blur-[100px]" />
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Text */}
          <motion.div initial="hidden" animate="visible" variants={stagger}>
            <motion.div variants={fadeUp} custom={0} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.08] bg-white/[0.05] backdrop-blur-sm mb-6">
              <div className="w-2 h-2 rounded-full bg-[var(--green)] animate-pulse" />
              <span className="text-[11px] text-[var(--text-secondary)] font-medium">
                CodeForge Hackathon 2026
              </span>
            </motion.div>

            <motion.h1 variants={fadeUp} custom={1} className="text-4xl md:text-5xl lg:text-[3.4rem] font-extrabold leading-tight tracking-tight drop-shadow-lg">
              AI-Powered{' '}
              <span className="bg-gradient-to-r from-indigo-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                Options Market
              </span>{' '}
              Intelligence
            </motion.h1>

            <motion.p variants={fadeUp} custom={2} className="mt-5 text-base md:text-lg text-[var(--text-secondary)] leading-relaxed max-w-xl">
              An advanced analytics platform that transforms complex options market data into clear insights using visualization and AI-driven pattern detection.
            </motion.p>

            <motion.div variants={fadeUp} custom={3} className="mt-6 grid grid-cols-2 gap-3 max-w-md">
              {[
                { label: 'Open Interest', icon: <BarChart3 size={14} /> },
                { label: 'Trading Volume', icon: <Layers size={14} /> },
                { label: 'Implied Volatility', icon: <Activity size={14} /> },
                { label: 'Market Sentiment', icon: <PieChart size={14} /> },
              ].map((item, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.08] backdrop-blur-sm"
                >
                  <span className="text-[var(--cyan)]">{item.icon}</span>
                  <span className="text-xs text-[var(--text-secondary)]">{item.label}</span>
                </div>
              ))}
            </motion.div>

            <motion.div variants={fadeUp} custom={4} className="mt-8 flex flex-wrap items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 text-white text-sm font-semibold flex items-center gap-2 shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 transition-all cursor-pointer"
              >
                Try Dashboard
                <ArrowRight size={16} />
              </motion.button>

              <motion.a
                whileHover={{ scale: 1.03 }}
                href="https://github.com/chetan137/CodeForge"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 rounded-xl border border-white/[0.12] bg-white/[0.05] backdrop-blur-sm text-sm font-medium flex items-center gap-2 hover:border-white/25 hover:bg-white/[0.08] transition-all cursor-pointer text-[var(--text-secondary)]"
              >
                <Github size={16} />
                View Source
              </motion.a>
            </motion.div>
          </motion.div>

          {/* Right: Dashboard preview with trading video */}
          <motion.div
            initial={{ opacity: 0, x: 40, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="relative"
          >
            <div className="relative rounded-2xl overflow-hidden border border-white/[0.1] shadow-2xl shadow-black/50 bg-[var(--bg-card)]">
              {/* Browser frame */}
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/[0.06] bg-[var(--bg-secondary)]/90 backdrop-blur-sm">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                  <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
                  <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
                </div>
                <div className="flex-1 mx-3">
                  <div className="bg-[var(--bg-primary)]/90 rounded-md px-3 py-1 text-[10px] text-[var(--text-muted)] font-mono truncate">
                    localhost:5173/dashboard
                  </div>
                </div>
              </div>

              {/* Stock market trading video inside the preview */}
              <div className="relative aspect-video bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-primary)]">
                <video
                  className="w-full h-full object-cover"
                  autoPlay
                  muted
                  loop
                  playsInline
                >
                  <source
                    src="https://videos.pexels.com/video-files/3945009/3945009-sd_640_360_25fps.mp4"
                    type="video/mp4"
                  />
                </video>

                {/* Dark overlay on the preview video */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/40 via-[var(--bg-primary)]/30 to-cyan-900/30" />

                {/* Play button overlay */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <div className="w-14 h-14 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center mb-3 hover:scale-110 hover:bg-white/20 transition-all cursor-pointer">
                    <Play size={20} className="text-white ml-0.5" />
                  </div>
                  <p className="text-[11px] text-white/60 font-medium">Live Trading Analytics</p>
                </div>

                {/* Simulated dashboard wireframe overlay */}
                <div className="absolute inset-0 p-3 pointer-events-none opacity-20">
                  <div className="grid grid-cols-4 gap-1.5 mb-2">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="h-8 rounded bg-white/[0.08] border border-white/[0.06]" />
                    ))}
                  </div>
                  <div className="grid grid-cols-2 gap-1.5">
                    <div className="h-24 rounded bg-white/[0.08] border border-white/[0.06]" />
                    <div className="h-24 rounded bg-white/[0.08] border border-white/[0.06]" />
                  </div>
                </div>
              </div>
            </div>

            {/* Floating badge */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
              className="absolute -bottom-4 -left-4 px-4 py-2.5 rounded-xl bg-[var(--bg-card)]/90 backdrop-blur-md border border-white/[0.1] shadow-xl flex items-center gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-[var(--green-dim)] flex items-center justify-center">
                <TrendingUp size={16} className="text-[var(--green)]" />
              </div>
              <div>
                <p className="text-xs font-semibold text-[var(--text-primary)]">PCR: 1.14</p>
                <p className="text-[10px] text-[var(--green)]">Bullish Sentiment</p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 }}
              className="absolute -top-3 -right-3 px-3 py-2 rounded-xl bg-[var(--bg-card)]/90 backdrop-blur-md border border-white/[0.1] shadow-xl flex items-center gap-2"
            >
              <Sparkles size={14} className="text-[var(--yellow)]" />
              <span className="text-[11px] font-medium text-[var(--yellow)]">AI Anomaly Detected</span>
            </motion.div>
          </motion.div>
        </div>

        {/* Stats row */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
          className="relative z-10 max-w-4xl mx-auto mt-20 grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {stats.map((s, i) => (
            <motion.div
              key={i}
              variants={fadeUp}
              custom={i}
              className="text-center p-5 rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-sm"
            >
              <p className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                {s.value}
              </p>
              <p className="text-[11px] text-[var(--text-muted)] mt-1 uppercase tracking-wider">
                {s.label}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ━━ FEATURES SECTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <section id="features" className="py-24 px-6 relative">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/[0.04] rounded-full blur-[150px]" />
        </div>

        <div className="relative max-w-7xl mx-auto">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="text-center mb-16">
            <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-widest text-[var(--cyan)] mb-3">
              Platform Capabilities
            </motion.p>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl md:text-4xl font-bold">
              Powerful Analytics,{' '}
              <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                Simplified
              </span>
            </motion.h2>
            <motion.p variants={fadeUp} custom={2} className="mt-4 text-[var(--text-secondary)] max-w-2xl mx-auto">
              Our platform provides institutional-grade analytics tools that help traders and analysts understand the derivatives market in real time.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-50px' }}
            variants={stagger}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-5"
          >
            {features.map((f, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                custom={i}
                whileHover={{ y: -6, transition: { duration: 0.25 } }}
                className="group relative p-6 rounded-2xl border border-white/[0.06] bg-[var(--bg-card)] hover:border-white/[0.12] transition-all duration-300 cursor-default"
              >
                {/* Glow on hover */}
                <div
                  className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    background: `radial-gradient(circle at 50% 0%, color-mix(in srgb, var(${f.color}) 8%, transparent), transparent 70%)`,
                  }}
                />

                <div className="relative">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                    style={{
                      background: `color-mix(in srgb, var(${f.color}) 12%, transparent)`,
                      color: `var(${f.color})`,
                    }}
                  >
                    {f.icon}
                  </div>
                  <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2">
                    {f.title}
                  </h3>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    {f.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ━━ USE CASES SECTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <section id="use-cases" className="py-24 px-6 bg-[var(--bg-secondary)]/50">
        <div className="max-w-7xl mx-auto">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left: Title */}
            <motion.div variants={fadeUp}>
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--green)] mb-3">
                Real-World Applications
              </p>
              <h2 className="text-3xl md:text-4xl font-bold leading-tight">
                Trading Intelligence{' '}
                <span className="bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent">
                  In Action
                </span>
              </h2>
              <p className="mt-4 text-[var(--text-secondary)] leading-relaxed">
                From retail traders to quantitative analysts — this platform provides the tools needed to navigate complex options markets with data-driven confidence.
              </p>

              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate('/dashboard')}
                className="mt-6 px-5 py-2.5 rounded-lg bg-[var(--green-dim)] border border-[var(--green)]/20 text-[var(--green)] text-xs font-semibold flex items-center gap-2 hover:bg-[var(--green)]/20 transition-colors cursor-pointer"
              >
                Explore Dashboard
                <ChevronRight size={14} />
              </motion.button>
            </motion.div>

            {/* Right: Use case cards */}
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={stagger}
              className="space-y-3"
            >
              {useCases.map((uc, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  custom={i}
                  whileHover={{ x: 6, transition: { duration: 0.2 } }}
                  className="flex items-center gap-4 p-4 rounded-xl border border-white/[0.06] bg-[var(--bg-card)]/60 hover:border-[var(--green)]/20 hover:bg-[var(--bg-card)] transition-all cursor-default"
                >
                  <div className="w-10 h-10 rounded-lg bg-[var(--green-dim)] flex items-center justify-center shrink-0">
                    <span className="text-[var(--green)]">{uc.icon}</span>
                  </div>
                  <p className="text-sm text-[var(--text-secondary)]">{uc.text}</p>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ━━ INNOVATION SECTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <section id="innovation" className="py-24 px-6 relative">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-cyan-500/[0.04] rounded-full blur-[130px]" />
        </div>

        <div className="relative max-w-7xl mx-auto">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="text-center mb-16">
            <motion.p variants={fadeUp} className="text-xs font-semibold uppercase tracking-widest text-[var(--yellow)] mb-3">
              What Makes Us Different
            </motion.p>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl md:text-4xl font-bold">
              Innovation in Options{' '}
              <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                Market Analytics
              </span>
            </motion.h2>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-5"
          >
            {innovations.map((item, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                custom={i}
                whileHover={{ scale: 1.03, transition: { duration: 0.25 } }}
                className="relative p-6 rounded-2xl border border-white/[0.06] bg-gradient-to-b from-[var(--bg-card)] to-[var(--bg-primary)] overflow-hidden group cursor-default"
              >
                {/* Top glow */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-1 rounded-b-full bg-gradient-to-r from-transparent via-[var(--yellow)]/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                <div className="w-10 h-10 rounded-lg bg-[var(--yellow-dim)] flex items-center justify-center mb-4">
                  <span className="text-[var(--yellow)]">{item.icon}</span>
                </div>
                <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2">
                  {item.title}
                </h3>
                <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                  {item.desc}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ━━ FOSS TECH STACK ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <section id="tech" className="py-24 px-6 bg-[var(--bg-secondary)]/50">
        <div className="max-w-5xl mx-auto">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="text-center mb-14">
            <motion.div variants={fadeUp} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.08] bg-white/[0.03] mb-4">
              <Code2 size={12} className="text-[var(--cyan)]" />
              <span className="text-[11px] text-[var(--text-secondary)] font-medium">
                100% Open Source
              </span>
            </motion.div>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl md:text-4xl font-bold">
              Built with{' '}
              <span className="bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                Open Source
              </span>{' '}
              Technologies
            </motion.h2>
            <motion.p variants={fadeUp} custom={2} className="mt-4 text-[var(--text-secondary)] max-w-2xl mx-auto">
              Every component of this platform leverages free and open-source software, promoting transparency, community collaboration, and innovation.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
            className="flex flex-wrap justify-center gap-4"
          >
            {techStack.map((tech, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                custom={i}
                whileHover={{ scale: 1.08, y: -4, transition: { duration: 0.2 } }}
                className="flex items-center gap-3 px-5 py-3 rounded-xl bg-[var(--bg-card)] border border-white/[0.06] hover:border-white/[0.15] transition-all cursor-default"
              >
                <div
                  className="w-3 h-3 rounded-full shrink-0"
                  style={{ backgroundColor: tech.color }}
                />
                <span className="text-sm font-medium text-[var(--text-primary)]">
                  {tech.name}
                </span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ━━ CTA SECTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <section className="py-28 px-6 relative">
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-r from-indigo-600/[0.08] to-cyan-600/[0.08] rounded-full blur-[130px]" />
        </div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
          className="relative max-w-3xl mx-auto text-center"
        >
          <motion.h2 variants={fadeUp} className="text-3xl md:text-4xl font-bold">
            Explore the Options{' '}
            <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              Analytics Dashboard
            </span>
          </motion.h2>
          <motion.p variants={fadeUp} custom={1} className="mt-4 text-[var(--text-secondary)] max-w-xl mx-auto">
            Dive into real-time options market data with interactive charts, AI-powered insights, and comprehensive analytics tools.
          </motion.p>

          <motion.div variants={fadeUp} custom={2} className="mt-8 flex flex-wrap justify-center gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/dashboard')}
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 text-white text-sm font-semibold flex items-center gap-2 shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 transition-all cursor-pointer"
            >
              Open Dashboard
              <ArrowRight size={16} />
            </motion.button>

            <motion.a
              whileHover={{ scale: 1.05 }}
              href="https://github.com/chetan137/CodeForge"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3.5 rounded-xl border border-white/[0.1] bg-white/[0.03] text-sm font-medium flex items-center gap-2 hover:border-white/20 transition-all cursor-pointer text-[var(--text-secondary)]"
            >
              <Github size={16} />
              GitHub Repository
              <ExternalLink size={12} />
            </motion.a>
          </motion.div>
        </motion.div>
      </section>

      {/* ━━ FOOTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */}
      <footer className="border-t border-white/[0.06] py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-md bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center">
              <TrendingUp size={14} className="text-white" />
            </div>
            <span className="text-xs text-[var(--text-muted)]">
              CodeForge Options Analytics · Built for CodeForge Hackathon 2026
            </span>
          </div>
          <p className="text-[11px] text-[var(--text-muted)]">
            Made with FOSS ❤️ · React · TailwindCSS · Recharts · Python
          </p>
        </div>
      </footer>
    </div>
  );
}
