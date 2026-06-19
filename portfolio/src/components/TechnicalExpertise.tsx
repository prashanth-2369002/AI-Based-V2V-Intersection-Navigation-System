import { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { Cpu, Code2, Zap, Wrench, GitBranch, Activity } from 'lucide-react'

interface TechnicalExpertiseProps {
  isDark: boolean
}

// ─── Core Expertise ────────────────────────────────────────────────────────────
const coreExpertise = [
  {
    icon: Cpu,
    title: 'Embedded Systems',
    description: 'Raspberry Pi, microcontrollers, real-time sensor fusion and hardware-software co-design.',
    color: '#00B4D8',
  },
  {
    icon: Zap,
    title: 'EV Technologies',
    description: 'Battery management, smart charging infrastructure, and EV powertrain systems.',
    color: '#48CAE4',
  },
  {
    icon: Activity,
    title: 'Industrial Automation',
    description: 'PLC programming, DCS operation, VFD configuration, and plant-floor maintenance.',
    color: '#0EA5E9',
  },
  {
    icon: GitBranch,
    title: 'AI Transportation',
    description: 'V2V/V2I communication, FCFS scheduling, trajectory prediction, and collision avoidance.',
    color: '#38BDF8',
  },
  {
    icon: Wrench,
    title: 'Power Electronics',
    description: 'Drives, converters, electrical safety, and industrial control panel design.',
    color: '#7DD3FC',
  },
]

// ─── Skill definitions ─────────────────────────────────────────────────────────
type Level = 'Expert' | 'Advanced' | 'Working Knowledge'

interface Skill {
  name: string
  level: Level
  projects?: string[]
}

interface Category {
  title: string
  icon: typeof Cpu
  color: string
  skills: Skill[]
}

const levelConfig: Record<Level, { dot: string; label: string; labelColor: string }> = {
  Expert:            { dot: '#00B4D8', label: 'Expert',            labelColor: '#00B4D8' },
  Advanced:          { dot: '#48CAE4', label: 'Advanced',          labelColor: '#48CAE4' },
  'Working Knowledge': { dot: '#94A3B8', label: 'Working Knowledge', labelColor: '#94A3B8' },
}

const categories: Category[] = [
  {
    title: 'Embedded & Hardware',
    icon: Cpu,
    color: '#00B4D8',
    skills: [
      { name: 'Raspberry Pi',       level: 'Expert',            projects: ['AI-Based V2V Negotiation System', 'Smart EV Charging System', 'IoT Automatic Door System'] },
      { name: 'PLC Systems',        level: 'Advanced',          projects: ['ITC Paper Machine 7 Automation'] },
      { name: 'DCS Systems',        level: 'Advanced',          projects: ['ITC Paper Machine 7 Automation'] },
      { name: 'Sensors & Actuators',level: 'Expert',            projects: ['IoT Automatic Door System', 'Smart EV Charging System'] },
      { name: 'Control Systems',    level: 'Advanced',          projects: ['AI-Based V2V Negotiation System'] },
      { name: 'Embedded Dev',       level: 'Expert',            projects: ['Microchip Embedded Internship'] },
    ],
  },
  {
    title: 'Programming',
    icon: Code2,
    color: '#48CAE4',
    skills: [
      { name: 'Python',  level: 'Expert',            projects: ['Traffic Coordination Algorithms', 'AI Internship — SkillDzire'] },
      { name: 'C',       level: 'Advanced',          projects: ['Microchip Embedded Internship'] },
      { name: 'MATLAB',  level: 'Working Knowledge', projects: ['Electrical System Simulation & Analysis'] },
    ],
  },
  {
    title: 'Electrical Engineering',
    icon: Zap,
    color: '#0EA5E9',
    skills: [
      { name: 'Power Electronics',  level: 'Advanced',          projects: ['Smart EV Charging System'] },
      { name: 'Motor Drives & VFD', level: 'Advanced',          projects: ['ITC Paper Machine 7 — Motor Maintenance'] },
      { name: 'Electrical Safety',  level: 'Expert',            projects: ['ITC Plant Operations'] },
      { name: 'Industrial Systems', level: 'Advanced',          projects: ['ITC Paper Machine 7 Unit'] },
    ],
  },
  {
    title: 'Software & Tools',
    icon: Wrench,
    color: '#38BDF8',
    skills: [
      { name: 'GitHub',             level: 'Advanced',          projects: ['All Engineering Projects'] },
      { name: 'VS Code',            level: 'Expert',            projects: ['Python & Embedded Development'] },
      { name: 'Thonny IDE',         level: 'Expert',            projects: ['Raspberry Pi Projects'] },
      { name: 'MS Office',          level: 'Advanced',          projects: ['ITC — Documentation & Reporting'] },
      { name: 'AutoCAD Electrical', level: 'Working Knowledge', projects: ['Electrical System Drafting'] },
    ],
  },
]

// ─── Skill Chip ───────────────────────────────────────────────────────────────
function SkillChip({ skill, categoryColor, isDark }: {
  skill: Skill
  categoryColor: string
  isDark: boolean
}) {
  const [open, setOpen] = useState(false)
  const cfg = levelConfig[skill.level]

  return (
    <div className="relative">
      <motion.button
        onClick={() => setOpen(o => !o)}
        whileHover={{ scale: 1.04, y: -2 }}
        whileTap={{ scale: 0.97 }}
        className={`flex items-center gap-2 px-3.5 py-2 rounded-xl border text-sm font-medium transition-all duration-200 cursor-pointer select-none ${
          open
            ? isDark
              ? 'border-accent/60 bg-accent/10 text-white'
              : 'border-accent/60 bg-accent/10 text-foreground'
            : isDark
              ? 'border-white/10 bg-white/5 text-slate-200 hover:border-white/25 hover:bg-white/10'
              : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
        }`}
      >
        {/* Level dot */}
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: cfg.dot }}
        />
        {skill.name}
      </motion.button>

      {/* Hover panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.97 }}
            transition={{ duration: 0.18 }}
            className={`absolute bottom-full left-0 mb-2 z-30 w-56 rounded-xl border p-3.5 shadow-xl ${
              isDark
                ? 'bg-[#0E2F44] border-accent/25 shadow-black/40'
                : 'bg-white border-slate-200 shadow-slate-200/80'
            }`}
          >
            {/* Skill name + level */}
            <div className="flex items-center justify-between mb-2">
              <span className={`font-heading font-semibold text-sm ${isDark ? 'text-white' : 'text-foreground'}`}>
                {skill.name}
              </span>
              <span
                className="text-xs font-mono px-2 py-0.5 rounded-full border"
                style={{ color: cfg.labelColor, borderColor: `${cfg.dot}40`, backgroundColor: `${cfg.dot}10` }}
              >
                {cfg.label}
              </span>
            </div>

            {/* Project associations */}
            {skill.projects && skill.projects.length > 0 && (
              <div>
                <p className={`text-xs font-mono mb-1.5 ${isDark ? 'text-slate-500' : 'text-muted'}`}>
                  Used in:
                </p>
                <ul className="space-y-1">
                  {skill.projects.map(p => (
                    <li key={p} className="flex items-start gap-1.5">
                      <span className="mt-1 flex-shrink-0 w-1 h-1 rounded-full" style={{ backgroundColor: categoryColor }} />
                      <span className={`text-xs leading-snug ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{p}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── Category Card ────────────────────────────────────────────────────────────
function CategoryCard({ category, isDark, index }: {
  category: Category
  isDark: boolean
  index: number
}) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })
  const Icon = category.icon

  const expertCount   = category.skills.filter(s => s.level === 'Expert').length
  const advancedCount = category.skills.filter(s => s.level === 'Advanced').length
  const wkCount       = category.skills.filter(s => s.level === 'Working Knowledge').length

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.55, delay: index * 0.1 }}
      className={`rounded-2xl border p-6 flex flex-col gap-5 transition-all duration-300 ${
        isDark
          ? 'bg-[#0E2F44]/60 border-white/8 hover:border-accent/30'
          : 'bg-white border-slate-200 hover:border-accent/30 shadow-sm hover:shadow-md'
      }`}
    >
      {/* Header */}
      <div className="flex items-center gap-3">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center border"
          style={{ backgroundColor: `${category.color}12`, borderColor: `${category.color}30` }}
        >
          <Icon size={20} style={{ color: category.color }} />
        </div>
        <div>
          <h3 className={`font-heading font-semibold text-base ${isDark ? 'text-white' : 'text-foreground'}`}>
            {category.title}
          </h3>
          <p className={`text-xs ${isDark ? 'text-slate-500' : 'text-muted'}`}>
            {category.skills.length} skills
          </p>
        </div>
      </div>

      {/* Chips */}
      <div className="flex flex-wrap gap-2">
        {category.skills.map(skill => (
          <SkillChip
            key={skill.name}
            skill={skill}
            categoryColor={category.color}
            isDark={isDark}
          />
        ))}
      </div>

      {/* Level summary */}
      <div className={`flex items-center gap-4 pt-4 border-t text-xs ${
        isDark ? 'border-white/5 text-slate-500' : 'border-slate-100 text-muted'
      }`}>
        {expertCount > 0 && (
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: levelConfig.Expert.dot }} />
            {expertCount} Expert
          </span>
        )}
        {advancedCount > 0 && (
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: levelConfig.Advanced.dot }} />
            {advancedCount} Advanced
          </span>
        )}
        {wkCount > 0 && (
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: levelConfig['Working Knowledge'].dot }} />
            {wkCount} Working Knowledge
          </span>
        )}
      </div>
    </motion.div>
  )
}

// ─── Core Expertise Card ──────────────────────────────────────────────────────
function CoreCard({ item, isDark, index }: {
  item: typeof coreExpertise[0]
  isDark: boolean
  index: number
}) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })
  const Icon = item.icon

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ y: -4 }}
      className={`group relative rounded-2xl border p-5 overflow-hidden cursor-default transition-all duration-300 ${
        isDark
          ? 'bg-[#0E2F44]/60 border-white/8 hover:border-accent/40'
          : 'bg-white border-slate-200 hover:border-accent/40 shadow-sm hover:shadow-md'
      }`}
    >
      {/* Subtle bg glow on hover */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"
        style={{ background: `radial-gradient(ellipse at top left, ${item.color}08, transparent 70%)` }}
      />

      <div className="relative z-10">
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center border mb-4"
          style={{ backgroundColor: `${item.color}12`, borderColor: `${item.color}30` }}
        >
          <Icon size={22} style={{ color: item.color }} />
        </div>
        <h4 className={`font-heading font-semibold text-base mb-1.5 ${isDark ? 'text-white' : 'text-foreground'}`}>
          {item.title}
        </h4>
        <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-muted'}`}>
          {item.description}
        </p>
      </div>
    </motion.div>
  )
}

// ─── Legend ───────────────────────────────────────────────────────────────────
function Legend({ isDark }: { isDark: boolean }) {
  return (
    <div className={`flex flex-wrap items-center gap-x-6 gap-y-2 text-xs ${isDark ? 'text-slate-500' : 'text-muted'}`}>
      <span className="font-mono uppercase tracking-wider">Experience level:</span>
      {(Object.entries(levelConfig) as [Level, typeof levelConfig[Level]][]).map(([level, cfg]) => (
        <span key={level} className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.dot }} />
          {cfg.label}
        </span>
      ))}
      <span className={`ml-auto text-xs ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
        Click any chip for project context
      </span>
    </div>
  )
}

// ─── Main Export ──────────────────────────────────────────────────────────────
export default function TechnicalExpertise({ isDark }: TechnicalExpertiseProps) {
  const headerRef = useRef(null)
  const headerInView = useInView(headerRef, { once: true, margin: '-100px' })

  return (
    <section
      id="skills"
      className={`section-padding ${isDark ? 'bg-primary' : 'bg-surface'}`}
    >
      <div className="container-max space-y-14">

        {/* ── Section header ── */}
        <div className="text-center" ref={headerRef}>
          <motion.span
            initial={{ opacity: 0 }}
            animate={headerInView ? { opacity: 1 } : {}}
            className="font-mono text-xs tracking-[0.25em] uppercase text-accent"
          >
            02. Skills
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={headerInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1 }}
            className={`font-heading text-3xl sm:text-4xl font-bold mt-2 ${isDark ? 'text-white' : 'text-foreground'}`}
          >
            Technical Expertise
          </motion.h2>
          <motion.div
            initial={{ scaleX: 0 }}
            animate={headerInView ? { scaleX: 1 } : {}}
            transition={{ delay: 0.2 }}
            className="w-16 h-1 bg-gradient-to-r from-accent to-highlight mx-auto mt-4 rounded-full"
          />
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={headerInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3 }}
            className={`mt-4 text-base max-w-xl mx-auto ${isDark ? 'text-slate-400' : 'text-muted'}`}
          >
            Skills validated through real deployments — internships, academic projects, and industry work.
          </motion.p>
        </div>

        {/* ── Core Expertise ── */}
        <div>
          <motion.p
            initial={{ opacity: 0, x: -10 }}
            animate={headerInView ? { opacity: 1, x: 0 } : {}}
            transition={{ delay: 0.35 }}
            className={`font-mono text-xs uppercase tracking-widest mb-5 ${isDark ? 'text-slate-500' : 'text-muted'}`}
          >
            Core Expertise
          </motion.p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {coreExpertise.map((item, i) => (
              <CoreCard key={item.title} item={item} isDark={isDark} index={i} />
            ))}
          </div>
        </div>

        {/* ── Divider ── */}
        <div className={`h-px ${isDark ? 'bg-white/5' : 'bg-slate-100'}`} />

        {/* ── Skill categories ── */}
        <div>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
            <motion.p
              initial={{ opacity: 0, x: -10 }}
              animate={headerInView ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: 0.4 }}
              className={`font-mono text-xs uppercase tracking-widest ${isDark ? 'text-slate-500' : 'text-muted'}`}
            >
              Skills by Domain
            </motion.p>
            <motion.div
              initial={{ opacity: 0 }}
              animate={headerInView ? { opacity: 1 } : {}}
              transition={{ delay: 0.5 }}
            >
              <Legend isDark={isDark} />
            </motion.div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {categories.map((cat, i) => (
              <CategoryCard key={cat.title} category={cat} isDark={isDark} index={i} />
            ))}
          </div>
        </div>

      </div>
    </section>
  )
}
