import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Briefcase, Settings, Activity, FileText, Wrench, CheckCircle } from 'lucide-react'

interface ExperienceProps {
  isDark: boolean
}

const responsibilities = [
  { icon: Settings, text: 'Motor maintenance — troubleshooting 3-phase induction motors and synchronous motors' },
  { icon: Activity, text: 'VFD systems — configuration, programming, and fault diagnosis of Variable Frequency Drives' },
  { icon: Wrench, text: 'PLC systems — programming, monitoring, and maintaining Siemens SIMATIC PLC units' },
  { icon: Activity, text: 'DCS systems — operating and maintaining Distributed Control Systems for Paper Machine 7' },
  { icon: CheckCircle, text: 'Troubleshooting — diagnosing electrical faults across the paper production unit' },
  { icon: FileText, text: 'Documentation — creating maintenance logs, SOPs, and equipment condition reports' },
  { icon: Wrench, text: 'Control panel testing — performing routine checks and calibration of industrial control panels' },
]

function IndustrialViz({ isDark }: { isDark: boolean }) {
  const blocks = [
    { label: 'PLC', color: '#00B4D8', x: 20, y: 30 },
    { label: 'DCS', color: '#48CAE4', x: 60, y: 20 },
    { label: 'VFD', color: '#0EA5E9', x: 80, y: 55 },
    { label: 'MTR', color: '#38BDF8', x: 40, y: 65 },
    { label: 'HMI', color: '#00B4D8', x: 15, y: 65 },
  ]

  return (
    <div className="relative w-full h-full overflow-hidden">
      <svg className="absolute inset-0 w-full h-full opacity-30">
        {blocks.map((b, i) =>
          blocks.slice(i + 1).map((b2, j) => (
            <motion.line
              key={`${i}-${j}`}
              x1={`${b.x}%`} y1={`${b.y}%`}
              x2={`${b2.x}%`} y2={`${b2.y}%`}
              stroke="#00B4D8" strokeWidth="1" strokeDasharray="3 5"
              animate={{ strokeDashoffset: [15, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear', delay: i * 0.5 }}
            />
          ))
        )}
      </svg>
      {blocks.map((block, i) => (
        <motion.div
          key={block.label}
          className="absolute rounded-xl flex flex-col items-center justify-center border-2"
          style={{
            left: `${block.x}%`,
            top: `${block.y}%`,
            transform: 'translate(-50%, -50%)',
            width: 52,
            height: 52,
            borderColor: `${block.color}50`,
            backgroundColor: `${block.color}10`,
          }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.15, duration: 0.5 }}
          whileHover={{ scale: 1.15 }}
        >
          <motion.div
            className="w-1.5 h-1.5 rounded-full mb-1"
            style={{ backgroundColor: block.color }}
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
          />
          <span className="font-mono text-xs font-bold" style={{ color: block.color }}>{block.label}</span>
        </motion.div>
      ))}
      {/* Paper machine animation */}
      <motion.div
        className={`absolute bottom-6 left-0 right-0 mx-4 h-2 rounded-full overflow-hidden ${isDark ? 'bg-white/5' : 'bg-slate-200'}`}
      >
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-accent/30 via-accent to-accent/30"
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          style={{ width: '60%' }}
        />
      </motion.div>
      <div className={`absolute bottom-2 left-0 right-0 text-center font-mono text-xs ${isDark ? 'text-accent/40' : 'text-accent/60'}`}>
        Paper Machine 7
      </div>
    </div>
  )
}

export default function Experience({ isDark }: ExperienceProps) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.08 } },
  }
  const item = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0, transition: { duration: 0.5 } },
  }

  return (
    <section
      id="experience"
      className={`section-padding ${isDark ? 'bg-primary' : 'bg-white'}`}
    >
      <div className="container-max">
        <div className="text-center mb-16" ref={ref}>
          <motion.span
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="font-mono text-xs tracking-[0.25em] uppercase text-accent"
          >
            04. Experience
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1 }}
            className={`font-heading text-3xl sm:text-4xl font-bold mt-2 ${isDark ? 'text-white' : 'text-foreground'}`}
          >
            Industrial Experience
          </motion.h2>
          <motion.div
            initial={{ scaleX: 0 }}
            animate={inView ? { scaleX: 1 } : {}}
            transition={{ delay: 0.2 }}
            className="w-16 h-1 bg-gradient-to-r from-accent to-highlight mx-auto mt-4 rounded-full"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start">
          {/* Main experience card - 3 cols */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7 }}
            className={`lg:col-span-3 rounded-2xl border overflow-hidden ${
              isDark ? 'bg-secondary/50 border-accent/20' : 'bg-surface border-slate-200'
            }`}
          >
            {/* Header */}
            <div
              className="p-6 border-b"
              style={{
                background: isDark
                  ? 'linear-gradient(135deg, rgba(0,180,216,0.08), transparent)'
                  : 'linear-gradient(135deg, rgba(0,180,216,0.05), transparent)',
                borderColor: isDark ? 'rgba(0,180,216,0.15)' : '#E2E8F0',
              }}
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-accent/10 border border-accent/30 flex items-center justify-center flex-shrink-0">
                  <Briefcase size={22} className="text-accent" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className={`font-heading font-bold text-xl ${isDark ? 'text-white' : 'text-foreground'}`}>
                      Electrical Intern
                    </h3>
                    <span className="px-2 py-0.5 rounded-full bg-accent/10 text-accent text-xs font-mono border border-accent/20">
                      Full-time Internship
                    </span>
                  </div>
                  <p className="text-accent font-semibold mt-0.5">ITC Limited</p>
                  <p className={`text-sm mt-0.5 ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                    Paper Machine 7 Unit
                  </p>
                  <div className="flex items-center gap-1.5 mt-2">
                    <span className={`font-mono text-xs ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                      Dec 2023 – Jun 2024
                    </span>
                    <span className={`text-xs ${isDark ? 'text-slate-500' : 'text-muted'}`}>•</span>
                    <span className={`font-mono text-xs ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                      7 months
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Responsibilities */}
            <div className="p-6">
              <h4 className={`font-heading font-semibold text-sm uppercase tracking-wide mb-4 ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                Responsibilities
              </h4>
              <motion.ul
                variants={container}
                initial="hidden"
                animate={inView ? 'show' : 'hidden'}
                className="space-y-3"
              >
                {responsibilities.map((resp, i) => {
                  const Icon = resp.icon
                  return (
                    <motion.li
                      key={i}
                      variants={item}
                      className={`flex items-start gap-3 p-3 rounded-xl border transition-all group cursor-default hover:border-accent/30 ${
                        isDark
                          ? 'border-white/5 hover:bg-accent/5'
                          : 'border-slate-100 hover:bg-accent/5'
                      }`}
                    >
                      <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:bg-accent/20 transition-colors">
                        <Icon size={13} className="text-accent" />
                      </div>
                      <span className={`text-sm leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
                        {resp.text}
                      </span>
                    </motion.li>
                  )
                })}
              </motion.ul>
            </div>
          </motion.div>

          {/* Right column - 2 cols */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="lg:col-span-2 space-y-6"
          >
            {/* Industrial visualization */}
            <div
              className={`rounded-2xl border overflow-hidden h-64 ${
                isDark ? 'bg-secondary/50 border-accent/20' : 'bg-surface border-slate-200'
              }`}
            >
              <div className={`px-4 py-3 border-b flex items-center gap-2 ${isDark ? 'border-accent/10' : 'border-slate-200'}`}>
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="font-mono text-xs text-accent/70">industrial_plant.sim</span>
              </div>
              <div className="h-full p-4">
                <IndustrialViz isDark={isDark} />
              </div>
            </div>

            {/* Key skills gained */}
            <div className={`p-5 rounded-2xl border ${isDark ? 'bg-secondary/50 border-accent/20' : 'bg-surface border-slate-200'}`}>
              <h4 className={`font-heading font-semibold text-sm mb-4 ${isDark ? 'text-white' : 'text-foreground'}`}>
                Skills Gained
              </h4>
              <div className="flex flex-wrap gap-2">
                {['PLC Programming', 'DCS Operation', 'VFD Systems', 'Motor Maintenance', 'Electrical Safety', 'SCADA', 'Documentation'].map(skill => (
                  <span
                    key={skill}
                    className={`px-2.5 py-1 rounded-lg text-xs border font-mono ${
                      isDark
                        ? 'border-accent/25 text-accent/80 bg-accent/5'
                        : 'border-accent/30 text-accent bg-accent/5'
                    }`}
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Company tag */}
            <div className={`p-5 rounded-2xl border text-center ${isDark ? 'bg-accent/5 border-accent/20' : 'bg-accent/5 border-accent/20'}`}>
              <p className={`text-xs font-mono mb-1 ${isDark ? 'text-slate-500' : 'text-muted'}`}>Organization</p>
              <p className="font-heading font-bold text-accent text-xl">ITC Limited</p>
              <p className={`text-xs mt-1 ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                One of India's foremost multi-business enterprises
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
