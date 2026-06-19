import { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import {
  Github, ExternalLink, Star, ChevronDown,
  GitBranch, Clock, Layers, Zap, Wifi,
  Activity, Battery, Radio, Eye
} from 'lucide-react'

interface ProjectsProps {
  isDark: boolean
}

// ─── Animated Visualization: V2V Intersection ────────────────────────────────
function V2VVisualization({ isDark }: { isDark: boolean }) {
  const [activeNode, setActiveNode] = useState(0)
  const nodes = [
    { id: 'EV-1', x: '14%', y: '28%', color: '#00B4D8' },
    { id: 'EV-2', x: '74%', y: '18%', color: '#48CAE4' },
    { id: 'RSU',  x: '50%', y: '52%', color: '#0EA5E9' },
    { id: 'Pi',   x: '18%', y: '70%', color: '#38BDF8' },
    { id: 'EV-3', x: '78%', y: '66%', color: '#7DD3FC' },
  ]
  const edges = [
    [0, 2], [1, 2], [2, 3], [2, 4], [0, 1],
  ]

  return (
    <div className="relative w-full h-full">
      <svg className="absolute inset-0 w-full h-full">
        <defs>
          <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#00B4D8" stopOpacity="0" />
            <stop offset="50%"  stopColor="#00B4D8" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#00B4D8" stopOpacity="0" />
          </linearGradient>
        </defs>
        {edges.map(([a, b], i) => (
          <motion.line
            key={i}
            x1={nodes[a].x} y1={nodes[a].y}
            x2={nodes[b].x} y2={nodes[b].y}
            stroke="url(#edgeGrad)" strokeWidth="1" strokeDasharray="5 7"
            animate={{ strokeDashoffset: [28, 0] }}
            transition={{ duration: 2 + i * 0.4, repeat: Infinity, ease: 'linear', delay: i * 0.3 }}
          />
        ))}
      </svg>

      {nodes.map((node, i) => (
        <motion.div
          key={node.id}
          className="absolute"
          style={{ left: node.x, top: node.y, transform: 'translate(-50%, -50%)' }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: i * 0.12 + 0.4 }}
        >
          <motion.div
            animate={{ y: [0, -7, 0] }}
            transition={{ duration: 3 + i * 0.6, repeat: Infinity, ease: 'easeInOut', delay: i * 0.4 }}
          >
            <motion.div
              className="absolute rounded-full border border-current opacity-40"
              style={{ color: node.color, width: 44, height: 44, top: -8, left: -8 }}
              animate={{ scale: [1, 2.2], opacity: [0.4, 0] }}
              transition={{ duration: 2.2, repeat: Infinity, delay: i * 0.45 }}
            />
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center border-2 cursor-pointer"
              style={{ borderColor: node.color, backgroundColor: `${node.color}18` }}
              onClick={() => setActiveNode(i)}
            >
              <span className="text-[8px] font-mono font-bold" style={{ color: node.color }}>
                {node.id[0]}
              </span>
            </div>
            <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 font-mono text-[9px] whitespace-nowrap" style={{ color: node.color }}>
              {node.id}
            </div>
          </motion.div>
        </motion.div>
      ))}

      <motion.div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-accent"
        animate={{ scale: [0, 5, 0], opacity: [0.9, 0] }}
        transition={{ duration: 3, repeat: Infinity }}
      />

      <div className={`absolute bottom-2 left-2 right-2 rounded-lg p-2.5 border font-mono text-[10px] backdrop-blur-sm ${
        isDark ? 'bg-black/50 border-accent/15 text-accent/80' : 'bg-white/80 border-accent/30 text-accent'
      }`}>
        <div className="flex items-center gap-1.5 mb-1">
          <motion.div className="w-1.5 h-1.5 rounded-full bg-green-400" animate={{ opacity: [1, 0.2, 1] }} transition={{ duration: 1.4, repeat: Infinity }} />
          <span className="text-green-400 font-semibold">SYSTEM ACTIVE</span>
        </div>
        <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 opacity-70 text-[9px]">
          <span>Nodes: 5/5 online</span><span>Latency: 12ms</span>
          <span>FCFS: enabled</span><span>AI predict: ON</span>
        </div>
      </div>
    </div>
  )
}

// ─── Animated Visualization: EV Charging ────────────────────────────────────
function EVChargingVisualization({ isDark }: { isDark: boolean }) {
  const [charge, setCharge] = useState(0.62)

  return (
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
      {/* Energy flow lines from top */}
      {[0, 1, 2].map(i => (
        <motion.div
          key={i}
          className="absolute w-0.5 rounded-full"
          style={{
            left: `${30 + i * 20}%`,
            top: 0,
            height: 80,
            background: 'linear-gradient(180deg, #00B4D8, transparent)',
          }}
          animate={{ opacity: [0, 0.8, 0], scaleY: [0, 1, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, delay: i * 0.5, ease: 'easeIn' }}
        />
      ))}

      <div className="flex flex-col items-center gap-4 w-full px-8 mt-4">
        {/* Charging station icon */}
        <div className={`relative w-24 h-20 rounded-2xl border-2 flex flex-col items-center justify-center gap-1 ${
          isDark ? 'bg-secondary border-accent/40' : 'bg-slate-100 border-accent/50'
        }`}>
          <motion.div
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.2, repeat: Infinity }}
          >
            <Zap size={24} className="text-accent" />
          </motion.div>
          <span className="font-mono text-[10px] text-accent">CHARGING</span>
          {/* Connector cable */}
          <motion.div
            className="absolute -bottom-5 left-1/2 w-0.5 h-5 -translate-x-1/2"
            style={{ background: 'linear-gradient(180deg, #00B4D8, #48CAE4)' }}
            animate={{ scaleY: [0.8, 1, 0.8] }}
            transition={{ duration: 1.2, repeat: Infinity }}
          />
        </div>

        {/* Battery block */}
        <div className={`w-full rounded-2xl border-2 p-4 ${
          isDark ? 'bg-secondary/60 border-accent/30' : 'bg-white border-accent/30'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-1.5">
              <Battery size={14} className="text-accent" />
              <span className={`font-mono text-xs font-bold ${isDark ? 'text-white' : 'text-foreground'}`}>
                BATTERY PACK
              </span>
            </div>
            <motion.span
              className="font-mono text-sm font-bold text-accent"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 1.2, repeat: Infinity }}
            >
              {Math.round(charge * 100)}%
            </motion.span>
          </div>

          {/* Battery bar */}
          <div className={`relative h-5 rounded-lg overflow-hidden border ${
            isDark ? 'bg-black/30 border-accent/20' : 'bg-slate-100 border-slate-300'
          }`}>
            <motion.div
              className="h-full rounded-lg"
              style={{
                width: `${charge * 100}%`,
                background: charge > 0.8
                  ? 'linear-gradient(90deg, #10B981, #34D399)'
                  : charge > 0.4
                    ? 'linear-gradient(90deg, #00B4D8, #48CAE4)'
                    : 'linear-gradient(90deg, #F59E0B, #FCD34D)',
              }}
              animate={{ width: [`${charge * 100}%`, `${Math.min(charge * 100 + 3, 100)}%`, `${charge * 100}%`] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            {/* Shimmer */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              animate={{ x: ['-100%', '200%'] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
            />
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-2 mt-3">
            {[
              { label: 'Voltage', value: '400V' },
              { label: 'Current', value: '120A' },
              { label: 'Temp', value: '28°C' },
            ].map(stat => (
              <div key={stat.label} className={`text-center p-1.5 rounded-lg ${isDark ? 'bg-black/20' : 'bg-slate-50'}`}>
                <div className="font-mono text-xs font-bold text-accent">{stat.value}</div>
                <div className={`text-[9px] ${isDark ? 'text-slate-500' : 'text-muted'}`}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Floating energy particles */}
      {[0, 1, 2, 3].map(i => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-accent"
          style={{ left: `${25 + i * 18}%`, top: '60%' }}
          animate={{ y: [0, -40, -80], opacity: [0, 1, 0], scale: [0.5, 1.5, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, delay: i * 0.4, ease: 'easeOut' }}
        />
      ))}

      <div className={`absolute bottom-2 left-2 right-2 rounded-lg p-2 border font-mono text-[10px] backdrop-blur-sm ${
        isDark ? 'bg-black/50 border-accent/15 text-accent/80' : 'bg-white/80 border-accent/30 text-accent'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <motion.div className="w-1.5 h-1.5 rounded-full bg-green-400" animate={{ opacity: [1, 0.2, 1] }} transition={{ duration: 1.2, repeat: Infinity }} />
            <span className="text-green-400">CHARGING ACTIVE</span>
          </div>
          <span className="opacity-60">ETA: 42 min</span>
        </div>
      </div>
    </div>
  )
}

// ─── Animated Visualization: IoT Door ───────────────────────────────────────
function IoTDoorVisualization({ isDark }: { isDark: boolean }) {
  const [doorOpen, setDoorOpen] = useState(false)
  const [detected, setDetected] = useState(false)

  // cycle detection
  useState(() => {
    const t = setInterval(() => {
      setDetected(true)
      setTimeout(() => { setDoorOpen(true) }, 700)
      setTimeout(() => { setDoorOpen(false); setDetected(false) }, 3500)
    }, 5000)
    return () => clearInterval(t)
  })

  return (
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
      {/* Sensor signal rings */}
      <div className="absolute top-6 right-8">
        <div className="relative">
          {[0, 1, 2].map(i => (
            <motion.div
              key={i}
              className="absolute rounded-full border"
              style={{
                width: 14 + i * 16,
                height: 14 + i * 16,
                top: -(7 + i * 8),
                left: -(7 + i * 8),
                borderColor: detected ? '#00B4D8' : '#64748B',
              }}
              animate={detected ? { scale: [1, 1.3, 1], opacity: [0.7, 0.2, 0.7] } : { opacity: 0.2 }}
              transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.3 }}
            />
          ))}
          <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
            detected ? 'border-accent bg-accent/15' : isDark ? 'border-slate-600 bg-slate-700' : 'border-slate-300 bg-slate-100'
          }`}>
            <Radio size={14} className={detected ? 'text-accent' : isDark ? 'text-slate-500' : 'text-muted'} />
          </div>
          <span className={`absolute -bottom-5 left-1/2 -translate-x-1/2 font-mono text-[9px] whitespace-nowrap ${
            detected ? 'text-accent' : isDark ? 'text-slate-500' : 'text-muted'
          }`}>PIR</span>
        </div>
      </div>

      {/* Eye / motion detection */}
      <div className="absolute top-6 left-8">
        <motion.div
          animate={detected ? { scale: [1, 1.15, 1] } : {}}
          transition={{ duration: 0.5, repeat: Infinity }}
          className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
            detected ? 'border-accent bg-accent/15' : isDark ? 'border-slate-600 bg-slate-700' : 'border-slate-300 bg-slate-100'
          }`}
        >
          <Eye size={14} className={detected ? 'text-accent' : isDark ? 'text-slate-500' : 'text-muted'} />
        </motion.div>
        <span className={`block text-center font-mono text-[9px] mt-1 ${detected ? 'text-accent' : isDark ? 'text-slate-500' : 'text-muted'}`}>
          ULTRASONIC
        </span>
      </div>

      {/* Door frame */}
      <div className="relative mt-4">
        {/* Frame */}
        <div className={`relative w-28 h-36 border-4 rounded-t-2xl flex items-end justify-center overflow-hidden ${
          isDark ? 'border-slate-600 bg-slate-800/40' : 'border-slate-400 bg-slate-100'
        }`}>
          {/* Door panel */}
          <motion.div
            className="absolute inset-0 rounded-t-lg"
            style={{ originX: 0 }}
            animate={{ scaleX: doorOpen ? 0.08 : 1 }}
            transition={{ type: 'spring', stiffness: 120, damping: 20, duration: 0.6 }}
          >
            <div className={`w-full h-full rounded-t-lg border-r-2 flex flex-col items-center justify-center gap-2 ${
              isDark ? 'bg-[#0E2F44] border-accent/30' : 'bg-white border-slate-200'
            }`}>
              <div className={`w-12 h-1 rounded-full ${isDark ? 'bg-accent/20' : 'bg-slate-200'}`} />
              <div className={`w-12 h-1 rounded-full ${isDark ? 'bg-accent/20' : 'bg-slate-200'}`} />
              {/* Knob */}
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: doorOpen ? '#10B981' : '#94A3B8' }}
              />
            </div>
          </motion.div>

          {/* Interior visible when open */}
          <AnimatePresence>
            {doorOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 flex items-center justify-center"
              >
                <div className="text-green-400 font-mono text-xs text-center">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.6, repeat: 2 }}
                  >✓</motion.div>
                  <div className="text-[9px]">ACCESS</div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Floor */}
        <div className={`h-2 w-36 -mx-4 rounded-b ${isDark ? 'bg-slate-700' : 'bg-slate-300'}`} />
      </div>

      {/* IoT signal lines */}
      {detected && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute top-12 left-14 right-14"
        >
          {[0, 1].map(i => (
            <motion.div
              key={i}
              className="absolute h-px bg-gradient-to-r from-accent via-accent/60 to-transparent"
              style={{ top: i * 6, width: '100%' }}
              animate={{ x: ['-100%', '100%'], opacity: [0, 1, 0] }}
              transition={{ duration: 1, repeat: Infinity, delay: i * 0.4 }}
            />
          ))}
        </motion.div>
      )}

      <div className={`absolute bottom-2 left-2 right-2 rounded-lg p-2 border font-mono text-[10px] backdrop-blur-sm ${
        isDark ? 'bg-black/50 border-accent/15 text-accent/80' : 'bg-white/80 border-accent/30 text-accent'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <motion.div
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: detected ? '#10B981' : '#64748B' }}
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1.2, repeat: Infinity }}
            />
            <span style={{ color: detected ? '#10B981' : '#64748B' }}>
              {detected ? (doorOpen ? 'ACCESS GRANTED' : 'MOTION DETECTED') : 'STANDBY'}
            </span>
          </div>
          <span className="opacity-50">IoT v2.1</span>
        </div>
      </div>
    </div>
  )
}

// ─── Project data ─────────────────────────────────────────────────────────────
const projects = [
  {
    id: 'v2v',
    title: 'AI-Based V2V Negotiation System for Safe Intersection Navigation in EVs',
    badge: 'Flagship Project',
    badgeColor: '#F59E0B',
    status: 'Active Development',
    statusColor: '#10B981',
    description:
      'Intelligent intersection management system using Raspberry Pi for autonomous vehicle coordination. Implements AI-driven trajectory prediction and real-time V2V/V2I communication to eliminate collision risks.',
    highlights: [
      'V2V (Vehicle-to-Vehicle) communication protocol',
      'V2I (Vehicle-to-Infrastructure) integration',
      'FCFS-based right-of-way allocation algorithm',
      'AI trajectory prediction with ML models',
      'Collision avoidance with real-time response',
      'Smart traffic negotiation engine',
    ],
    tags: ['Raspberry Pi', 'Python', 'AI/ML', 'V2V', 'FCFS', 'IoT', 'Embedded'],
    metrics: [
      { label: 'Collision Reduction', value: '95%' },
      { label: 'Response Time', value: '<50ms' },
      { label: 'V2V Nodes', value: '5 EVs' },
      { label: 'Algorithm', value: 'FCFS+AI' },
    ],
    repoInfo: {
      url: 'https://github.com/prashanth-2369002/AI-Based-V2V-Intersection-Navigation-System',
      label: 'prashanth-2369002 / AI-Based-V2V-Intersection-Navigation-System',
      architecture: 'Raspberry Pi + FCFS Scheduler + ML Predictor',
      lastUpdated: 'June 2026',
      techStack: 'Python · OpenCV · Socket.io · NumPy',
    },
    color: '#00B4D8',
    icon: Activity,
    featured: true,
    Visualization: V2VVisualization,
  },
  {
    id: 'ev-charging',
    title: 'Smart EV Charging System with Battery Management',
    badge: null,
    badgeColor: null,
    status: 'Completed',
    statusColor: '#48CAE4',
    description:
      'Automated EV charging infrastructure with integrated payment processing and advanced battery health monitoring. Provides real-time analytics on charging patterns and energy efficiency.',
    highlights: [
      'Real-time battery monitoring & diagnostics',
      'Smart adaptive charging profiles',
      'Integrated payment & billing system',
      'Energy analytics dashboard',
      'Battery health prognostics',
    ],
    tags: ['Raspberry Pi', 'Python', 'IoT', 'Battery BMS', 'Power Electronics'],
    metrics: [
      { label: 'Charge Efficiency', value: '98%' },
      { label: 'BMS Safety', value: 'Active' },
      { label: 'Monitoring', value: 'Real-time' },
    ],
    repoInfo: {
      url: 'https://github.com/prashanth-2369002',
      label: 'prashanth-2369002 / EV-Charging-System',
      architecture: 'Raspberry Pi + BMS Module + Payment API',
      lastUpdated: 'May 2026',
      techStack: 'Python · GPIO · SQLite · Tkinter',
    },
    color: '#48CAE4',
    icon: Zap,
    featured: false,
    Visualization: EVChargingVisualization,
  },
  {
    id: 'iot-door',
    title: 'IoT-Based Automatic Door System',
    badge: null,
    badgeColor: null,
    status: 'Completed',
    statusColor: '#48CAE4',
    description:
      'Smart access control system using PIR and ultrasonic sensors with wireless IoT communication. Features layered safety mechanisms and real-time status monitoring.',
    highlights: [
      'PIR + ultrasonic dual-sensor detection',
      'Wireless IoT communication',
      'Automated access control logic',
      'Multi-layer safety override',
    ],
    tags: ['IoT', 'Sensors', 'Raspberry Pi', 'Python', 'Automation', 'Wireless'],
    metrics: [
      { label: 'Detection Range', value: '5m' },
      { label: 'Response', value: '<200ms' },
      { label: 'Safety Layers', value: '3-Level' },
    ],
    repoInfo: {
      url: 'https://github.com/prashanth-2369002',
      label: 'prashanth-2369002 / IoT-Door-System',
      architecture: 'Raspberry Pi + Dual Sensors + Servo Motor',
      lastUpdated: 'Apr 2026',
      techStack: 'Python · RPi.GPIO · MQTT · MicroPython',
    },
    color: '#0EA5E9',
    icon: Wifi,
    featured: false,
    Visualization: IoTDoorVisualization,
  },
]

// ─── Repo Info Panel ─────────────────────────────────────────────────────────
function RepoPanel({ repo, color, isDark }: {
  repo: typeof projects[0]['repoInfo']
  color: string
  isDark: boolean
}) {
  const rows = [
    { icon: Github,  label: 'Repository',   value: repo.label },
    { icon: Layers,  label: 'Architecture', value: repo.architecture },
    { icon: Clock,   label: 'Last Updated', value: repo.lastUpdated },
    { icon: GitBranch, label: 'Tech Stack', value: repo.techStack },
  ]

  return (
    <div className={`rounded-xl border p-4 space-y-2.5 ${
      isDark ? 'bg-black/20 border-white/5' : 'bg-slate-50 border-slate-100'
    }`}>
      {rows.map(({ icon: Icon, label, value }) => (
        <div key={label} className="flex items-start gap-2.5">
          <div className="w-5 h-5 flex items-center justify-center flex-shrink-0 mt-0.5">
            <Icon size={12} style={{ color }} />
          </div>
          <div className="min-w-0">
            <span className={`block text-[10px] font-mono uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-muted'}`}>
              {label}
            </span>
            <span className={`text-xs ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
              {value}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}

// ─── Project Card ─────────────────────────────────────────────────────────────
function ProjectCard({ project, isDark, index }: {
  project: typeof projects[0]
  isDark: boolean
  index: number
}) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })
  const [expanded, setExpanded] = useState(false)
  const [tooltip, setTooltip] = useState(false)
  const { Visualization } = project

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.65, delay: index * 0.12 }}
      className={`rounded-2xl border overflow-hidden flex flex-col transition-all duration-300 ${
        project.featured
          ? isDark
            ? 'border-accent/40 shadow-xl shadow-accent/10'
            : 'border-accent/50 shadow-xl shadow-accent/10'
          : isDark
            ? 'border-white/8 hover:border-white/15'
            : 'border-slate-200 hover:border-slate-300 shadow-sm'
      } ${isDark ? 'bg-[#0E2F44]/60' : 'bg-white'}`}
    >
      {/* ── Visual panel ── */}
      <div
        className="relative h-52 overflow-hidden flex-shrink-0 cursor-pointer group"
        style={{ background: `linear-gradient(135deg, ${project.color}12, ${project.color}04)` }}
      >
        {/* Lazy-mount visualization */}
        {inView && (
          <motion.div
            className="absolute inset-0 p-3 pt-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Visualization isDark={isDark} />
          </motion.div>
        )}

        {/* Fallback when not in view */}
        {!inView && (
          <div className="absolute inset-0 flex items-center justify-center opacity-20">
            <project.icon size={64} style={{ color: project.color }} />
          </div>
        )}

        {/* Top bar */}
        <div className={`absolute top-0 left-0 right-0 flex items-center justify-between px-3 py-2 ${
          isDark ? 'bg-black/30' : 'bg-white/60'
        } backdrop-blur-sm`}>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: `${project.color}60` }} />
            <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: `${project.color}40` }} />
            <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: `${project.color}20` }} />
            <span className={`ml-1 font-mono text-[9px] ${isDark ? 'text-slate-500' : 'text-muted'}`}>
              {project.id}.sim
            </span>
          </div>

          {/* Status pill */}
          <div className="flex items-center gap-1.5">
            <motion.div
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: project.statusColor }}
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1.8, repeat: Infinity }}
            />
            <span className="font-mono text-[10px]" style={{ color: project.statusColor }}>
              {project.status}
            </span>
          </div>
        </div>

        {/* Featured badge */}
        {project.badge && (
          <div
            className="absolute top-8 left-3 flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-semibold border"
            style={{ color: project.badgeColor!, borderColor: `${project.badgeColor}40`, backgroundColor: `${project.badgeColor}15` }}
          >
            <Star size={10} fill="currentColor" />
            {project.badge}
          </div>
        )}
      </div>

      {/* ── Content ── */}
      <div className="p-5 flex flex-col gap-4 flex-1">
        {/* Title */}
        <div>
          <h3 className={`font-heading font-bold text-base leading-snug ${isDark ? 'text-white' : 'text-foreground'}`}>
            {project.title}
          </h3>
        </div>

        {/* Description */}
        <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-muted'}`}>
          {project.description}
        </p>

        {/* Metrics */}
        <div className={`grid gap-2 ${project.metrics.length === 4 ? 'grid-cols-4' : 'grid-cols-3'}`}>
          {project.metrics.map(m => (
            <div
              key={m.label}
              className={`p-2 rounded-xl text-center border ${
                isDark ? 'bg-black/20 border-white/5' : 'bg-surface border-slate-100'
              }`}
            >
              <div className="font-mono font-bold text-xs" style={{ color: project.color }}>{m.value}</div>
              <div className={`text-[9px] mt-0.5 leading-tight ${isDark ? 'text-slate-500' : 'text-muted'}`}>{m.label}</div>
            </div>
          ))}
        </div>

        {/* Repo info panel */}
        <RepoPanel repo={project.repoInfo} color={project.color} isDark={isDark} />

        {/* Expandable highlights */}
        <div>
          <button
            onClick={() => setExpanded(e => !e)}
            className="flex items-center gap-1.5 text-xs font-medium"
            style={{ color: project.color }}
          >
            Key Highlights
            <motion.span animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
              <ChevronDown size={13} />
            </motion.span>
          </button>
          <AnimatePresence>
            {expanded && (
              <motion.ul
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.22 }}
                className="overflow-hidden mt-2 space-y-1.5"
              >
                {project.highlights.map(h => (
                  <li key={h} className={`flex items-start gap-2 text-xs ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
                    <span style={{ color: project.color }} className="mt-0.5 flex-shrink-0">▸</span>
                    {h}
                  </li>
                ))}
              </motion.ul>
            )}
          </AnimatePresence>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5">
          {project.tags.map(tag => (
            <span
              key={tag}
              className={`px-2 py-0.5 rounded-lg font-mono text-[10px] border ${
                isDark
                  ? 'border-white/8 text-slate-400 bg-white/4'
                  : 'border-slate-200 text-slate-500 bg-slate-50'
              }`}
            >
              {tag}
            </span>
          ))}
        </div>

        {/* CTA buttons */}
        <div className="flex gap-2.5 mt-auto pt-1">
          {/* GitHub button with tooltip */}
          <div className="flex-1 relative">
            <motion.a
              href={project.repoInfo.url}
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onMouseEnter={() => setTooltip(true)}
              onMouseLeave={() => setTooltip(false)}
              className={`w-full flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-medium border transition-all ${
                isDark
                  ? 'border-white/12 text-slate-300 hover:text-white hover:border-accent/40 hover:bg-accent/5'
                  : 'border-slate-200 text-slate-600 hover:border-accent/40 hover:text-accent hover:bg-accent/5'
              }`}
            >
              <Github size={14} />
              View on GitHub
              <ExternalLink size={11} className="opacity-50" />
            </motion.a>

            {/* Tooltip */}
            <AnimatePresence>
              {tooltip && (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 2 }}
                  className={`absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 rounded-lg text-xs whitespace-nowrap z-20 border ${
                    isDark ? 'bg-[#071A2E] border-accent/20 text-slate-300' : 'bg-white border-slate-200 text-slate-700 shadow-lg'
                  }`}
                >
                  View complete source code and documentation
                  <div
                    className="absolute top-full left-1/2 -translate-x-1/2 w-2 h-2 rotate-45 border-b border-r"
                    style={{ marginTop: -5, borderColor: isDark ? 'rgba(0,180,216,0.2)' : '#E2E8F0', backgroundColor: isDark ? '#071A2E' : 'white' }}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <motion.a
            href={project.repoInfo.url}
            target="_blank"
            rel="noopener noreferrer"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-medium text-white"
            style={{ background: `linear-gradient(135deg, ${project.color}, ${project.color}BB)` }}
          >
            Details
            <ExternalLink size={11} />
          </motion.a>
        </div>
      </div>
    </motion.div>
  )
}

// ─── Section ──────────────────────────────────────────────────────────────────
export default function Projects({ isDark }: ProjectsProps) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="projects"
      className={`section-padding ${isDark ? 'bg-secondary/30' : 'bg-slate-50'}`}
    >
      <div className="container-max">
        <div className="text-center mb-14" ref={ref}>
          <motion.span
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="font-mono text-xs tracking-[0.25em] uppercase text-accent"
          >
            03. Projects
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1 }}
            className={`font-heading text-3xl sm:text-4xl font-bold mt-2 ${isDark ? 'text-white' : 'text-foreground'}`}
          >
            Featured Projects
          </motion.h2>
          <motion.div
            initial={{ scaleX: 0 }}
            animate={inView ? { scaleX: 1 } : {}}
            transition={{ delay: 0.2 }}
            className="w-16 h-1 bg-gradient-to-r from-accent to-highlight mx-auto mt-4 rounded-full"
          />
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3 }}
            className={`mt-4 text-base max-w-xl mx-auto ${isDark ? 'text-slate-400' : 'text-muted'}`}
          >
            Engineering solutions from concept to deployment — AI transportation, EV infrastructure, and IoT automation.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-7">
          {projects.map((project, i) => (
            <ProjectCard key={project.id} project={project} isDark={isDark} index={i} />
          ))}
        </div>
      </div>
    </section>
  )
}
