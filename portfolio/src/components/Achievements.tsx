import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Trophy, Star, Users, Shield } from 'lucide-react'

interface AchievementsProps {
  isDark: boolean
}

const achievements = [
  {
    icon: Trophy,
    title: 'TCS iON NQT',
    value: '89.65%',
    subtitle: 'Cognitive Score',
    description: 'Scored 89.65% in TCS iON National Qualifier Test, demonstrating exceptional analytical and problem-solving capabilities.',
    color: '#F59E0B',
    bgColor: 'rgba(245,158,11,0.08)',
    borderColor: 'rgba(245,158,11,0.25)',
  },
  {
    icon: Star,
    title: 'State-Level Recognition',
    value: '1st',
    subtitle: 'Project Presentation',
    description: 'Presented engineering project at state-level competition, showcasing innovation in embedded systems and EV technology.',
    color: '#00B4D8',
    bgColor: 'rgba(0,180,216,0.08)',
    borderColor: 'rgba(0,180,216,0.25)',
  },
  {
    icon: Users,
    title: 'District Coordinator',
    value: 'Lead',
    subtitle: 'Sports Meet',
    description: 'Successfully led coordination of the District Sports Meet, managing logistics, scheduling, and inter-institution communications.',
    color: '#48CAE4',
    bgColor: 'rgba(72,202,228,0.08)',
    borderColor: 'rgba(72,202,228,0.25)',
  },
  {
    icon: Shield,
    title: 'NCC Certificate',
    value: '"A"',
    subtitle: 'National Cadet Corps',
    description: 'Earned NCC A Certificate, reflecting discipline, leadership, and commitment to national service and teamwork.',
    color: '#10B981',
    bgColor: 'rgba(16,185,129,0.08)',
    borderColor: 'rgba(16,185,129,0.25)',
  },
]

function AchievementCard({ achievement, index, parentInView }: {
  achievement: typeof achievements[0]
  index: number
  parentInView: boolean
}) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-50px' })
  const Icon = achievement.icon
  const active = inView || parentInView

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={active ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      whileHover={{ y: -6, scale: 1.02 }}
      className="relative rounded-2xl border p-6 overflow-hidden transition-all duration-300"
      style={{ borderColor: active ? achievement.borderColor : undefined }}
    >
      {/* Background glow */}
      <div
        className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-10 blur-2xl"
        style={{ backgroundColor: achievement.color }}
      />

      {/* Icon */}
      <motion.div
        whileHover={{ rotate: 15, scale: 1.1 }}
        className="w-12 h-12 rounded-xl flex items-center justify-center border-2 mb-4"
        style={{ backgroundColor: achievement.bgColor, borderColor: achievement.borderColor }}
      >
        <Icon size={22} style={{ color: achievement.color }} />
      </motion.div>

      {/* Value */}
      <motion.div
        className="font-heading font-bold text-4xl"
        style={{ color: achievement.color }}
        initial={{ scale: 0.5, opacity: 0 }}
        animate={active ? { scale: 1, opacity: 1 } : {}}
        transition={{ type: 'spring', stiffness: 200, delay: 0.2 + index * 0.1 }}
      >
        {achievement.value}
      </motion.div>

      {/* Title */}
      <h3 className="font-heading font-semibold text-base mt-2 text-inherit">
        {achievement.title}
      </h3>
      <p className="text-sm font-medium mb-3" style={{ color: achievement.color }}>
        {achievement.subtitle}
      </p>
      <p className="text-xs leading-relaxed opacity-70">
        {achievement.description}
      </p>

      {/* Bottom accent line */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5 rounded-full"
        style={{ backgroundColor: achievement.color }}
        initial={{ width: 0 }}
        animate={active ? { width: '100%' } : {}}
        transition={{ duration: 0.8, delay: index * 0.1 + 0.3 }}
      />
    </motion.div>
  )
}

export default function Achievements({ isDark }: AchievementsProps) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="achievements"
      className={`section-padding ${isDark ? 'bg-primary' : 'bg-white'}`}
    >
      <div className="container-max">
        <div className="text-center mb-16" ref={ref}>
          <motion.span
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="font-mono text-xs tracking-[0.25em] uppercase text-accent"
          >
            06. Achievements
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1 }}
            className={`font-heading text-3xl sm:text-4xl font-bold mt-2 ${isDark ? 'text-white' : 'text-foreground'}`}
          >
            Awards & Achievements
          </motion.h2>
          <motion.div
            initial={{ scaleX: 0 }}
            animate={inView ? { scaleX: 1 } : {}}
            transition={{ delay: 0.2 }}
            className="w-16 h-1 bg-gradient-to-r from-accent to-highlight mx-auto mt-4 rounded-full"
          />
        </div>

        <div
          className={`grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 ${
            isDark ? '[&_.font-heading]:text-white [&_.text-xs]:text-slate-400' : '[&_.font-heading]:text-foreground [&_.text-xs]:text-muted'
          }`}
        >
          {achievements.map((achievement, i) => (
            <AchievementCard
              key={achievement.title}
              achievement={achievement}
              index={i}
              parentInView={inView}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
