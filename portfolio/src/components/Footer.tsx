import { motion } from 'framer-motion'
import { Github, Linkedin, Mail, Zap, ArrowUp } from 'lucide-react'

interface FooterProps {
  isDark: boolean
}

const quickLinks = [
  { label: 'About', href: '#about' },
  { label: 'Skills', href: '#skills' },
  { label: 'Projects', href: '#projects' },
  { label: 'Experience', href: '#experience' },
  { label: 'Certifications', href: '#certifications' },
  { label: 'Contact', href: '#contact' },
]

const socials = [
  { icon: Github, href: 'https://github.com/prashanth-2369002', label: 'GitHub' },
  { icon: Linkedin, href: 'https://linkedin.com/in/mallaprashanth', label: 'LinkedIn' },
  { icon: Mail, href: 'mailto:prashanthmalla920@gmail.com', label: 'Email' },
]

export default function Footer({ isDark }: FooterProps) {
  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <footer className={`${isDark ? 'bg-primary border-accent/10' : 'bg-white border-slate-200'} border-t`}>
      {/* Quote banner */}
      <div
        className="py-8 px-4 text-center"
        style={{ background: isDark ? 'linear-gradient(180deg, rgba(0,180,216,0.05), transparent)' : 'linear-gradient(180deg, rgba(0,180,216,0.03), transparent)' }}
      >
        <motion.blockquote
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className={`font-heading font-medium text-lg sm:text-xl italic ${isDark ? 'text-slate-300' : 'text-slate-600'}`}
        >
          "Engineering intelligent systems for a smarter future."
        </motion.blockquote>
      </div>

      <div className={`border-t ${isDark ? 'border-white/5' : 'border-slate-100'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            {/* Brand */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-highlight flex items-center justify-center">
                  <Zap size={16} className="text-white" />
                </div>
                <span className={`font-heading font-bold ${isDark ? 'text-white' : 'text-foreground'}`}>
                  Malla Prashanth
                </span>
              </div>
              <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                Electrical & Electronics Engineer specializing in Embedded Systems, EV Technologies, and AI Transportation.
              </p>
              <div className="flex gap-3">
                {socials.map(({ icon: Icon, href, label }) => (
                  <motion.a
                    key={label}
                    href={href}
                    target={href.startsWith('http') ? '_blank' : undefined}
                    rel={href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    whileHover={{ scale: 1.15, y: -2 }}
                    aria-label={label}
                    className={`p-2 rounded-lg border transition-all ${
                      isDark
                        ? 'border-white/10 text-slate-400 hover:text-accent hover:border-accent/40 hover:bg-accent/5'
                        : 'border-slate-200 text-muted hover:text-accent hover:border-accent/40'
                    }`}
                  >
                    <Icon size={16} />
                  </motion.a>
                ))}
              </div>
            </div>

            {/* Quick links */}
            <div>
              <h4 className={`font-heading font-semibold text-sm mb-4 ${isDark ? 'text-white' : 'text-foreground'}`}>
                Quick Links
              </h4>
              <ul className="grid grid-cols-2 gap-x-4 gap-y-2">
                {quickLinks.map(link => (
                  <li key={link.href}>
                    <a
                      href={link.href}
                      onClick={(e) => handleNavClick(e, link.href)}
                      className={`text-sm transition-colors hover:text-accent ${isDark ? 'text-slate-400' : 'text-muted'}`}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Status + back to top */}
            <div className="space-y-4">
              <div className={`p-4 rounded-xl border ${isDark ? 'bg-secondary/40 border-accent/15' : 'bg-surface border-slate-200'}`}>
                <div className="flex items-center gap-2 mb-1.5">
                  <motion.div
                    className="w-2 h-2 rounded-full bg-green-400"
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <span className={`text-xs font-mono uppercase tracking-wide ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                    Status
                  </span>
                </div>
                <p className={`text-sm font-medium ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                  Open to Opportunities
                </p>
                <p className={`text-xs mt-0.5 ${isDark ? 'text-slate-500' : 'text-muted'}`}>
                  Internships · Full-time · Projects
                </p>
              </div>

              <motion.button
                onClick={scrollToTop}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium border transition-all ${
                  isDark
                    ? 'border-white/10 text-slate-300 hover:text-accent hover:border-accent/40'
                    : 'border-slate-200 text-slate-600 hover:text-accent hover:border-accent/40'
                }`}
              >
                <ArrowUp size={14} />
                Back to Top
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className={`border-t ${isDark ? 'border-white/5' : 'border-slate-100'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className={`text-xs ${isDark ? 'text-slate-500' : 'text-muted'}`}>
            © {new Date().getFullYear()} Malla Prashanth. All rights reserved.
          </p>
          <p className={`text-xs font-mono ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
            Built with{' '}
            <span className="text-accent">React</span>
            {' '}+{' '}
            <span className="text-accent">TypeScript</span>
            {' '}+{' '}
            <span className="text-accent">Framer Motion</span>
          </p>
        </div>
      </div>
    </footer>
  )
}
