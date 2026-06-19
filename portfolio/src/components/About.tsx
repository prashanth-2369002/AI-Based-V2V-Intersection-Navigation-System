import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { GraduationCap, Award, Target, BookOpen } from 'lucide-react'

interface AboutProps {
  isDark: boolean
}

const focusAreas = [
  { label: 'Embedded Systems', icon: '⚡' },
  { label: 'EV Technology', icon: '🔋' },
  { label: 'AI Transportation', icon: '🤖' },
  { label: 'Power Electronics', icon: '⚙️' },
  { label: 'Industrial Automation', icon: '🏭' },
  { label: 'Smart Infrastructure', icon: '🏙️' },
]

const timeline = [
  {
    year: '2022 – Present',
    title: 'B.Tech in Electrical & Electronics Engineering',
    institution: 'KL University, Vijayawada',
    detail: 'CGPA: 9.30',
    icon: GraduationCap,
    color: '#00B4D8',
  },
  {
    year: '2019 – 2022',
    title: 'Diploma in Electrical & Electronics Engineering',
    institution: 'Government Polytechnic Kothagudem',
    detail: 'CGPA: 9.62',
    icon: BookOpen,
    color: '#48CAE4',
  },
]

const stats = [
  { label: 'B.Tech CGPA', value: '9.30', suffix: '', icon: Award },
  { label: 'Diploma CGPA', value: '9.62', suffix: '', icon: GraduationCap },
  { label: 'Projects Built', value: '3', suffix: '+', icon: Target },
  { label: 'TCS NQT Score', value: '89.65', suffix: '%', icon: Award },
]

function AnimatedCounter({ value, suffix }: { value: string; suffix: string }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })
  const numVal = parseFloat(value)

  return (
    <span ref={ref}>
      {inView ? (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {value}{suffix}
        </motion.span>
      ) : (
        <span>0{suffix}</span>
      )}
    </span>
  )
}

export default function About({ isDark }: AboutProps) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.12 } },
  }
  const item = {
    hidden: { opacity: 0, y: 30 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6 } },
  }

  return (
    <section
      id="about"
      className={`section-padding ${isDark ? 'bg-secondary/30' : 'bg-white'}`}
    >
      <div className="container-max" ref={ref}>
        {/* Section header */}
        <motion.div
          variants={container}
          initial="hidden"
          animate={inView ? 'show' : 'hidden'}
          className="text-center mb-16"
        >
          <motion.span
            variants={item}
            className="font-mono text-xs tracking-[0.25em] uppercase text-accent"
          >
            01. About
          </motion.span>
          <motion.h2
            variants={item}
            className={`font-heading text-3xl sm:text-4xl font-bold mt-2 ${isDark ? 'text-white' : 'text-foreground'}`}
          >
            Engineering Background
          </motion.h2>
          <motion.div
            variants={item}
            className="w-16 h-1 bg-gradient-to-r from-accent to-highlight mx-auto mt-4 rounded-full"
          />
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
          {/* Left: Bio + Stats */}
          <motion.div
            variants={container}
            initial="hidden"
            animate={inView ? 'show' : 'hidden'}
            className="space-y-8"
          >
            <motion.div variants={item}>
              <p className={`text-base leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
                I am a passionate Electrical &amp; Electronics Engineering student at{' '}
                <span className="text-accent font-medium">KL University, Vijayawada</span>, maintaining
                an exceptional academic record while building real-world expertise in intelligent
                transportation systems and embedded technologies.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
                My flagship project — an AI-Based V2V Negotiation System — demonstrates my ability
                to bridge theoretical knowledge with practical engineering solutions, targeting
                next-generation autonomous vehicle coordination.
              </p>
            </motion.div>

            {/* Stats grid */}
            <motion.div variants={item} className="grid grid-cols-2 gap-4">
              {stats.map((stat) => {
                const Icon = stat.icon
                return (
                  <motion.div
                    key={stat.label}
                    whileHover={{ scale: 1.02, y: -2 }}
                    className={`p-4 rounded-xl border transition-all ${
                      isDark
                        ? 'bg-primary border-accent/20 hover:border-accent/50'
                        : 'bg-surface border-slate-200 hover:border-accent/40'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Icon size={16} className="text-accent" />
                      <span className={`text-xs ${isDark ? 'text-slate-400' : 'text-muted'}`}>{stat.label}</span>
                    </div>
                    <div className="font-heading font-bold text-2xl text-gradient">
                      <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                    </div>
                  </motion.div>
                )
              })}
            </motion.div>

            {/* Focus areas */}
            <motion.div variants={item}>
              <h3 className={`font-heading font-semibold text-lg mb-4 ${isDark ? 'text-white' : 'text-foreground'}`}>
                Focus Areas
              </h3>
              <div className="flex flex-wrap gap-2">
                {focusAreas.map((area) => (
                  <motion.span
                    key={area.label}
                    whileHover={{ scale: 1.05 }}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-all cursor-default ${
                      isDark
                        ? 'border-accent/30 text-accent/80 bg-accent/5 hover:border-accent/60'
                        : 'border-accent/40 text-accent bg-accent/5 hover:bg-accent/10'
                    }`}
                  >
                    <span>{area.icon}</span>
                    {area.label}
                  </motion.span>
                ))}
              </div>
            </motion.div>
          </motion.div>

          {/* Right: Academic Timeline */}
          <motion.div
            variants={container}
            initial="hidden"
            animate={inView ? 'show' : 'hidden'}
            className="space-y-6"
          >
            <motion.h3
              variants={item}
              className={`font-heading font-semibold text-lg ${isDark ? 'text-white' : 'text-foreground'}`}
            >
              Academic Journey
            </motion.h3>

            <div className="relative space-y-6">
              {/* Vertical line */}
              <div className={`absolute left-6 top-0 bottom-0 w-px ${isDark ? 'bg-accent/20' : 'bg-accent/30'}`} />

              {timeline.map((item2, i) => {
                const Icon = item2.icon
                return (
                  <motion.div
                    key={i}
                    variants={item}
                    className="relative flex gap-6"
                  >
                    {/* Icon */}
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className="relative z-10 flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center border-2"
                      style={{ borderColor: item2.color, backgroundColor: `${item2.color}15` }}
                    >
                      <Icon size={20} style={{ color: item2.color }} />
                    </motion.div>

                    {/* Content */}
                    <motion.div
                      whileHover={{ x: 4 }}
                      className={`flex-1 p-5 rounded-xl border transition-all ${
                        isDark
                          ? 'bg-primary/60 border-accent/15 hover:border-accent/40'
                          : 'bg-surface border-slate-200 hover:border-accent/30'
                      }`}
                    >
                      <span className="font-mono text-xs text-accent mb-2 block">{item2.year}</span>
                      <h4 className={`font-heading font-semibold text-base mb-1 ${isDark ? 'text-white' : 'text-foreground'}`}>
                        {item2.title}
                      </h4>
                      <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-muted'}`}>{item2.institution}</p>
                      <div className="mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20">
                        <Award size={12} className="text-accent" />
                        <span className="font-mono text-xs font-bold text-accent">{item2.detail}</span>
                      </div>
                    </motion.div>
                  </motion.div>
                )
              })}
            </div>

            {/* Currently studying card */}
            <motion.div
              variants={item}
              className={`p-5 rounded-xl border-2 border-accent/40 ${
                isDark ? 'bg-accent/5' : 'bg-accent/5'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <motion.div
                  className="w-2 h-2 rounded-full bg-green-400"
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <span className="font-mono text-xs text-accent uppercase tracking-widest">Currently Enrolled</span>
              </div>
              <p className={`text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
                Final year B.Tech student actively seeking opportunities in{' '}
                <span className="text-accent font-medium">Embedded Systems</span>,{' '}
                <span className="text-accent font-medium">EV Technology</span>, and{' '}
                <span className="text-accent font-medium">Industrial Automation</span>.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
