import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Award, Cpu, Brain, ExternalLink } from 'lucide-react'

interface CertificationsProps {
  isDark: boolean
}

const certifications = [
  {
    title: 'Microchip Advanced Embedded System Developer',
    subtitle: 'Internship Certification',
    issuer: 'EduSkills & APSCHE',
    year: '2024',
    icon: Cpu,
    color: '#00B4D8',
    bgColor: 'rgba(0,180,216,0.08)',
    borderColor: 'rgba(0,180,216,0.25)',
    highlights: [
      'Embedded C programming',
      'Microchip PIC architecture',
      'Peripheral interfacing',
      'Real-time system design',
    ],
    badge: 'Embedded Systems',
  },
  {
    title: 'Artificial Intelligence Internship',
    subtitle: 'Industry Certification',
    issuer: 'SkillDzire',
    year: '2024',
    icon: Brain,
    color: '#48CAE4',
    bgColor: 'rgba(72,202,228,0.08)',
    borderColor: 'rgba(72,202,228,0.25)',
    highlights: [
      'Machine Learning fundamentals',
      'AI model development',
      'Python for AI/ML',
      'Data preprocessing & analysis',
    ],
    badge: 'Artificial Intelligence',
  },
]

export default function Certifications({ isDark }: CertificationsProps) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      id="certifications"
      className={`section-padding ${isDark ? 'bg-secondary/20' : 'bg-slate-50'}`}
    >
      <div className="container-max">
        <div className="text-center mb-16" ref={ref}>
          <motion.span
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="font-mono text-xs tracking-[0.25em] uppercase text-accent"
          >
            05. Certifications
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1 }}
            className={`font-heading text-3xl sm:text-4xl font-bold mt-2 ${isDark ? 'text-white' : 'text-foreground'}`}
          >
            Certifications & Training
          </motion.h2>
          <motion.div
            initial={{ scaleX: 0 }}
            animate={inView ? { scaleX: 1 } : {}}
            transition={{ delay: 0.2 }}
            className="w-16 h-1 bg-gradient-to-r from-accent to-highlight mx-auto mt-4 rounded-full"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {certifications.map((cert, i) => {
            const Icon = cert.icon
            return (
              <motion.div
                key={cert.title}
                initial={{ opacity: 0, y: 40 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: i * 0.15 }}
                whileHover={{ y: -6 }}
                className={`relative rounded-2xl border overflow-hidden transition-all duration-300 ${
                  isDark
                    ? 'bg-secondary/60 border-accent/20 hover:border-accent/50 shadow-lg shadow-black/20'
                    : 'bg-white border-slate-200 hover:border-accent/40 shadow-lg shadow-slate-100'
                }`}
              >
                {/* Top accent bar */}
                <div className="h-1 w-full" style={{ background: `linear-gradient(90deg, ${cert.color}, transparent)` }} />

                <div className="p-6">
                  {/* Icon + badge */}
                  <div className="flex items-start justify-between mb-5">
                    <motion.div
                      whileHover={{ rotate: 10, scale: 1.1 }}
                      className="w-14 h-14 rounded-2xl flex items-center justify-center border-2"
                      style={{ backgroundColor: cert.bgColor, borderColor: cert.borderColor }}
                    >
                      <Icon size={28} style={{ color: cert.color }} />
                    </motion.div>
                    <div className="flex flex-col items-end gap-1.5">
                      <span
                        className="px-3 py-1 rounded-full text-xs font-medium border"
                        style={{ color: cert.color, borderColor: cert.borderColor, backgroundColor: cert.bgColor }}
                      >
                        {cert.badge}
                      </span>
                      <span className={`font-mono text-xs ${isDark ? 'text-slate-500' : 'text-muted'}`}>
                        {cert.year}
                      </span>
                    </div>
                  </div>

                  {/* Title */}
                  <h3 className={`font-heading font-bold text-lg leading-snug mb-1 ${isDark ? 'text-white' : 'text-foreground'}`}>
                    {cert.title}
                  </h3>
                  <p className={`text-sm mb-1 ${isDark ? 'text-slate-400' : 'text-muted'}`}>{cert.subtitle}</p>
                  <div className="flex items-center gap-1.5 mb-5">
                    <Award size={13} style={{ color: cert.color }} />
                    <span className="text-sm font-medium" style={{ color: cert.color }}>{cert.issuer}</span>
                  </div>

                  {/* Highlights */}
                  <ul className="space-y-2 mb-5">
                    {cert.highlights.map((h) => (
                      <li key={h} className={`flex items-center gap-2 text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
                        <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: cert.color }} />
                        {h}
                      </li>
                    ))}
                  </ul>

                  {/* Verified badge */}
                  <div className={`flex items-center justify-between pt-4 border-t ${isDark ? 'border-white/5' : 'border-slate-100'}`}>
                    <div className="flex items-center gap-1.5">
                      <motion.div
                        className="w-2 h-2 rounded-full bg-green-400"
                        animate={{ opacity: [1, 0.3, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                      <span className={`text-xs ${isDark ? 'text-slate-500' : 'text-muted'}`}>Verified Certificate</span>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      className={`flex items-center gap-1 text-xs font-medium`}
                      style={{ color: cert.color }}
                    >
                      View <ExternalLink size={11} />
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
