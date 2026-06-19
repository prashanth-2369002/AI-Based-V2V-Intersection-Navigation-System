import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Github, Linkedin, Mail, Download, ArrowDown, ExternalLink } from 'lucide-react'

interface HeroProps {
  isDark: boolean
}

const typingPhrases = [
  'Embedded Systems',
  'V2V Communication',
  'Electric Vehicles',
  'Industrial Automation',
  'AI Transportation',
  'Raspberry Pi Projects',
]

function EngineeringGrid({ isDark }: { isDark: boolean }) {
  return (
    <div className="absolute inset-0 overflow-hidden">
      {/* Grid */}
      <div
        className="absolute inset-0 engineering-grid opacity-40"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 180, 216, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 180, 216, 0.08) 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
        }}
      />
      {/* Dot intersections */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `radial-gradient(circle, #00B4D8 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
        }}
      />
      {/* Radial gradient overlay */}
      <div
        className="absolute inset-0"
        style={{
          background: isDark
            ? 'radial-gradient(ellipse 80% 60% at 50% 50%, transparent 30%, #071A2E 100%)'
            : 'radial-gradient(ellipse 80% 60% at 50% 50%, transparent 30%, #F8FAFC 100%)',
        }}
      />
      {/* Animated accent lines */}
      <motion.div
        className="absolute top-1/4 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent"
        animate={{ opacity: [0.3, 0.7, 0.3] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute top-3/4 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent/20 to-transparent"
        animate={{ opacity: [0.2, 0.5, 0.2] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
      />
    </div>
  )
}

function FloatingNode({ x, y, delay, size = 8 }: { x: string; y: string; delay: number; size?: number }) {
  return (
    <motion.div
      className="absolute rounded-full bg-accent/40 border border-accent/60"
      style={{ left: x, top: y, width: size, height: size }}
      animate={{
        y: [0, -15, 0],
        opacity: [0.4, 1, 0.4],
        scale: [1, 1.2, 1],
      }}
      transition={{ duration: 3 + delay, repeat: Infinity, delay, ease: 'easeInOut' }}
    />
  )
}

function V2VVisualization({ isDark }: { isDark: boolean }) {
  const nodes = [
    { x: '10%', y: '30%', label: 'EV-1', delay: 0 },
    { x: '75%', y: '20%', label: 'EV-2', delay: 0.5 },
    { x: '50%', y: '55%', label: 'RSU', delay: 1 },
    { x: '20%', y: '70%', label: 'Pi', delay: 1.5 },
    { x: '80%', y: '65%', label: 'Sensor', delay: 2 },
  ]

  return (
    <div className="relative w-full h-full">
      {/* Connection lines */}
      <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 0 }}>
        <defs>
          <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00B4D8" stopOpacity="0" />
            <stop offset="50%" stopColor="#00B4D8" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#00B4D8" stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* Animated data packets along lines */}
        <motion.line x1="15%" y1="33%" x2="52%" y2="57%" stroke="url(#lineGrad)" strokeWidth="1" strokeDasharray="4 6"
          animate={{ strokeDashoffset: [24, 0] }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} />
        <motion.line x1="78%" y1="23%" x2="52%" y2="57%" stroke="url(#lineGrad)" strokeWidth="1" strokeDasharray="4 6"
          animate={{ strokeDashoffset: [24, 0] }} transition={{ duration: 2.5, repeat: Infinity, ease: 'linear', delay: 0.5 }} />
        <motion.line x1="15%" y1="33%" x2="78%" y2="23%" stroke="url(#lineGrad)" strokeWidth="1" strokeDasharray="4 6"
          animate={{ strokeDashoffset: [24, 0] }} transition={{ duration: 3, repeat: Infinity, ease: 'linear', delay: 1 }} />
        <motion.line x1="52%" y1="57%" x2="22%" y2="72%" stroke="url(#lineGrad)" strokeWidth="1" strokeDasharray="4 6"
          animate={{ strokeDashoffset: [24, 0] }} transition={{ duration: 2.2, repeat: Infinity, ease: 'linear', delay: 0.8 }} />
        <motion.line x1="52%" y1="57%" x2="82%" y2="67%" stroke="url(#lineGrad)" strokeWidth="1" strokeDasharray="4 6"
          animate={{ strokeDashoffset: [24, 0] }} transition={{ duration: 2.8, repeat: Infinity, ease: 'linear', delay: 1.2 }} />
      </svg>

      {/* Nodes */}
      {nodes.map((node, i) => (
        <motion.div
          key={i}
          className="absolute z-10"
          style={{ left: node.x, top: node.y, transform: 'translate(-50%, -50%)' }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: node.delay * 0.3 + 0.5, duration: 0.5 }}
        >
          <motion.div
            className="relative"
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 3 + i * 0.5, repeat: Infinity, delay: node.delay, ease: 'easeInOut' }}
          >
            {/* Pulse ring */}
            <motion.div
              className="absolute inset-0 rounded-full border border-accent/50"
              animate={{ scale: [1, 2.5], opacity: [0.5, 0] }}
              transition={{ duration: 2, repeat: Infinity, delay: node.delay }}
              style={{ width: 44, height: 44, top: -6, left: -6 }}
            />
            {/* Node body */}
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              isDark ? 'bg-secondary border-accent/60' : 'bg-white border-accent'
            } shadow-lg`}>
              <span className="text-accent font-mono text-xs font-bold">{node.label[0]}</span>
            </div>
            {/* Label */}
            <div className={`absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-mono whitespace-nowrap ${
              isDark ? 'text-accent/70' : 'text-accent'
            }`}>
              {node.label}
            </div>
          </motion.div>
        </motion.div>
      ))}

      {/* Central data pulse */}
      <motion.div
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-accent"
        animate={{ scale: [0, 3, 0], opacity: [0, 0.8, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeOut' }}
      />

      {/* Status panel */}
      <motion.div
        className={`absolute bottom-4 left-4 right-4 rounded-xl p-3 font-mono text-xs border ${
          isDark ? 'bg-black/40 border-accent/20 text-accent/80' : 'bg-white/80 border-accent/30 text-accent'
        } backdrop-blur-sm`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <motion.div
            className="w-2 h-2 rounded-full bg-green-400"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <span className="text-green-400">V2V SYSTEM ACTIVE</span>
        </div>
        <div className="grid grid-cols-2 gap-1 text-xs opacity-70">
          <span>Nodes: 5/5</span>
          <span>Latency: 12ms</span>
          <span>FCFS: ON</span>
          <span>AI: RUNNING</span>
        </div>
      </motion.div>
    </div>
  )
}

function TypingEffect({ phrases }: { phrases: string[] }) {
  const [currentPhrase, setCurrentPhrase] = useState(0)
  const [displayText, setDisplayText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [charIndex, setCharIndex] = useState(0)

  useEffect(() => {
    const phrase = phrases[currentPhrase]
    const speed = isDeleting ? 40 : 80

    const timer = setTimeout(() => {
      if (!isDeleting && charIndex < phrase.length) {
        setDisplayText(phrase.slice(0, charIndex + 1))
        setCharIndex(c => c + 1)
      } else if (!isDeleting && charIndex === phrase.length) {
        setTimeout(() => setIsDeleting(true), 2000)
      } else if (isDeleting && charIndex > 0) {
        setDisplayText(phrase.slice(0, charIndex - 1))
        setCharIndex(c => c - 1)
      } else if (isDeleting && charIndex === 0) {
        setIsDeleting(false)
        setCurrentPhrase(c => (c + 1) % phrases.length)
      }
    }, speed)

    return () => clearTimeout(timer)
  }, [charIndex, currentPhrase, isDeleting, phrases])

  return (
    <span>
      <span className="text-gradient">{displayText}</span>
      <span className="cursor-blink text-accent">|</span>
    </span>
  )
}

export default function Hero({ isDark }: HeroProps) {
  const heroRef = useRef<HTMLDivElement>(null)

  const socialLinks = [
    { icon: Github, label: 'GitHub', href: 'https://github.com/prashanth-2369002', color: 'hover:text-accent' },
    { icon: Linkedin, label: 'LinkedIn', href: 'https://linkedin.com/in/mallaprashanth', color: 'hover:text-accent' },
    { icon: Mail, label: 'Email', href: 'mailto:prashanthmalla920@gmail.com', color: 'hover:text-accent' },
  ]

  return (
    <section
      id="hero"
      ref={heroRef}
      className={`relative min-h-screen flex flex-col overflow-hidden ${
        isDark ? 'bg-primary' : 'bg-surface'
      }`}
    >
      <EngineeringGrid isDark={isDark} />

      {/* Floating accent particles */}
      <FloatingNode x="5%" y="20%" delay={0} size={6} />
      <FloatingNode x="92%" y="15%" delay={1} size={4} />
      <FloatingNode x="88%" y="80%" delay={2} size={7} />
      <FloatingNode x="3%" y="75%" delay={0.5} size={5} />

      {/* Top bar with name + links */}
      <div className="relative z-10 flex items-center justify-between px-6 pt-24 max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <span className={`font-mono text-xs tracking-[0.25em] uppercase ${isDark ? 'text-muted' : 'text-muted'}`}>
            Portfolio
          </span>
          <h2 className={`font-heading font-bold text-lg mt-0.5 ${isDark ? 'text-white' : 'text-foreground'}`}>
            MALLA PRASHANTH
          </h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="flex items-center gap-2"
        >
          <motion.a
            href="/resume.pdf"
            download
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-4 py-2 bg-accent text-white text-sm font-medium rounded-lg hover:bg-highlight transition-colors"
          >
            <Download size={14} />
            <span className="hidden sm:inline">Resume</span>
          </motion.a>

          {socialLinks.map(({ icon: Icon, label, href }) => (
            <motion.a
              key={label}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label={label}
              className={`p-2.5 rounded-lg border transition-all duration-200 ${
                isDark
                  ? 'border-white/10 text-slate-300 hover:text-accent hover:border-accent/40 hover:bg-accent/5'
                  : 'border-slate-200 text-slate-600 hover:text-accent hover:border-accent/40 hover:bg-accent/5'
              }`}
            >
              <Icon size={16} />
            </motion.a>
          ))}
        </motion.div>
      </div>

      {/* Main content */}
      <div className="relative z-10 flex-1 flex items-center">
        <div className="max-w-7xl mx-auto px-6 w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center py-12">
          {/* Left: Text */}
          <div className="space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.7 }}
            >
              <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-mono mb-6 ${
                isDark
                  ? 'border-accent/30 text-accent/80 bg-accent/5'
                  : 'border-accent/40 text-accent bg-accent/5'
              }`}>
                <motion.div
                  className="w-1.5 h-1.5 rounded-full bg-green-400"
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                Available for Opportunities
              </div>

              <h1 className={`font-heading text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight ${
                isDark ? 'text-white' : 'text-foreground'
              }`}>
                Electrical &<br />
                <span className="text-gradient">Electronics</span><br />
                Engineer
              </h1>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className={`text-lg ${isDark ? 'text-slate-300' : 'text-slate-600'}`}
            >
              Building Intelligent Transportation,<br />
              Embedded Systems &amp; EV Technologies
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.6 }}
              className="font-heading text-xl sm:text-2xl font-medium min-h-[2rem]"
            >
              <TypingEffect phrases={typingPhrases} />
            </motion.div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.6 }}
              className={`text-base leading-relaxed max-w-lg ${isDark ? 'text-slate-400' : 'text-muted'}`}
            >
              Motivated Electrical &amp; Electronics Engineering student with hands-on experience
              in industrial systems, embedded development, EV technologies and intelligent
              transportation systems.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9, duration: 0.6 }}
              className="flex flex-wrap gap-4"
            >
              <motion.a
                href="#projects"
                onClick={(e) => { e.preventDefault(); document.querySelector('#projects')?.scrollIntoView({ behavior: 'smooth' }) }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-6 py-3 bg-accent text-white font-semibold rounded-xl hover:bg-highlight transition-colors shadow-lg shadow-accent/20 flex items-center gap-2"
              >
                View Projects
                <ExternalLink size={16} />
              </motion.a>
              <motion.a
                href="#contact"
                onClick={(e) => { e.preventDefault(); document.querySelector('#contact')?.scrollIntoView({ behavior: 'smooth' }) }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-6 py-3 font-semibold rounded-xl border-2 border-accent text-accent hover:bg-accent hover:text-white transition-all flex items-center gap-2`}
              >
                Contact Me
                <Mail size={16} />
              </motion.a>
            </motion.div>
          </div>

          {/* Right: V2V Visualization */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className={`relative h-96 lg:h-[500px] rounded-2xl border overflow-hidden ${
              isDark
                ? 'bg-secondary/50 border-accent/20 shadow-2xl shadow-black/40'
                : 'bg-white border-slate-200 shadow-2xl shadow-slate-200/60'
            }`}
          >
            <div className={`absolute top-0 left-0 right-0 h-8 flex items-center gap-1.5 px-4 border-b ${
              isDark ? 'bg-black/20 border-accent/10' : 'bg-slate-50 border-slate-200'
            }`}>
              <div className="w-2.5 h-2.5 rounded-full bg-red-400/70" />
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-400/70" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-400/70" />
              <span className={`ml-3 font-mono text-xs ${isDark ? 'text-accent/50' : 'text-muted'}`}>
                v2v_intersection_sim.py
              </span>
            </div>
            <div className="pt-8 h-full">
              <V2VVisualization isDark={isDark} />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="relative z-10 flex flex-col items-center pb-8 gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
      >
        <span className={`font-mono text-xs tracking-widest ${isDark ? 'text-muted' : 'text-muted'}`}>
          SCROLL
        </span>
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <ArrowDown size={16} className="text-accent" />
        </motion.div>
      </motion.div>
    </section>
  )
}
