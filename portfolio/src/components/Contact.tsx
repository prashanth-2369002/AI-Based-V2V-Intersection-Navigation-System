import { useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import { Mail, Phone, Github, Linkedin, Copy, Check, Send, MapPin } from 'lucide-react'

interface ContactProps {
  isDark: boolean
}

const contactInfo = [
  {
    icon: Mail,
    label: 'Email',
    value: 'prashanthmalla920@gmail.com',
    href: 'mailto:prashanthmalla920@gmail.com',
    color: '#00B4D8',
    copyable: true,
  },
  {
    icon: Phone,
    label: 'Phone',
    value: '+91 70133 77812',
    href: 'tel:+917013377812',
    color: '#48CAE4',
    copyable: true,
  },
  {
    icon: Github,
    label: 'GitHub',
    value: 'github.com/prashanth-2369002',
    href: 'https://github.com/prashanth-2369002',
    color: '#0EA5E9',
    copyable: false,
  },
  {
    icon: Linkedin,
    label: 'LinkedIn',
    value: 'linkedin.com/in/mallaprashanth',
    href: 'https://linkedin.com/in/mallaprashanth',
    color: '#38BDF8',
    copyable: false,
  },
  {
    icon: MapPin,
    label: 'Location',
    value: 'Vijayawada, Andhra Pradesh, India',
    href: null,
    color: '#48CAE4',
    copyable: false,
  },
]

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.button
      onClick={handleCopy}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className="p-1.5 rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors"
      aria-label="Copy to clipboard"
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </motion.button>
  )
}

export default function Contact({ isDark }: ContactProps) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })
  const [formState, setFormState] = useState({ name: '', email: '', subject: '', message: '' })
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSending(true)
    await new Promise(r => setTimeout(r, 1500))
    setSending(false)
    setSent(true)
    setFormState({ name: '', email: '', subject: '', message: '' })
    setTimeout(() => setSent(false), 4000)
  }

  return (
    <section
      id="contact"
      className={`section-padding ${isDark ? 'bg-secondary/20' : 'bg-slate-50'}`}
    >
      <div className="container-max">
        <div className="text-center mb-16" ref={ref}>
          <motion.span
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="font-mono text-xs tracking-[0.25em] uppercase text-accent"
          >
            07. Contact
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1 }}
            className={`font-heading text-3xl sm:text-4xl font-bold mt-2 ${isDark ? 'text-white' : 'text-foreground'}`}
          >
            Get In Touch
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
            className={`mt-4 text-base max-w-lg mx-auto ${isDark ? 'text-slate-400' : 'text-muted'}`}
          >
            Interested in collaboration, internships, or full-time opportunities? Let's connect.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Contact info card */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7 }}
            className={`lg:col-span-2 rounded-2xl border p-6 relative overflow-hidden ${
              isDark
                ? 'bg-secondary/60 border-accent/20 backdrop-blur-sm'
                : 'bg-white border-slate-200 shadow-lg shadow-slate-100'
            }`}
          >
            {/* Glass background accent */}
            <div className="absolute top-0 right-0 w-40 h-40 rounded-full bg-accent/5 blur-3xl" />

            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-6">
                <motion.div
                  className="w-2 h-2 rounded-full bg-green-400"
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <span className="font-mono text-xs text-accent/70 uppercase tracking-widest">
                  Available for Opportunities
                </span>
              </div>

              <h3 className={`font-heading font-bold text-xl mb-6 ${isDark ? 'text-white' : 'text-foreground'}`}>
                Contact Information
              </h3>

              <div className="space-y-4">
                {contactInfo.map((info) => {
                  const Icon = info.icon
                  return (
                    <motion.div
                      key={info.label}
                      whileHover={{ x: 4 }}
                      className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                        isDark
                          ? 'border-white/5 hover:border-accent/20 hover:bg-accent/5'
                          : 'border-slate-100 hover:border-accent/20 hover:bg-accent/5'
                      }`}
                    >
                      <div
                        className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: `${info.color}15`, border: `1px solid ${info.color}30` }}
                      >
                        <Icon size={16} style={{ color: info.color }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-xs ${isDark ? 'text-slate-500' : 'text-muted'}`}>{info.label}</p>
                        {info.href ? (
                          <a
                            href={info.href}
                            target={info.href.startsWith('http') ? '_blank' : undefined}
                            rel={info.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                            className={`text-sm font-medium truncate block hover:text-accent transition-colors ${
                              isDark ? 'text-slate-200' : 'text-slate-700'
                            }`}
                          >
                            {info.value}
                          </a>
                        ) : (
                          <span className={`text-sm font-medium truncate block ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                            {info.value}
                          </span>
                        )}
                      </div>
                      {info.copyable && <CopyButton text={info.value} />}
                    </motion.div>
                  )
                })}
              </div>

              {/* Social quick links */}
              <div className="mt-6 pt-5 border-t flex gap-3 border-white/5">
                <motion.a
                  href="https://github.com/prashanth-2369002"
                  target="_blank"
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.1, y: -2 }}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium border transition-all ${
                    isDark
                      ? 'border-white/15 text-slate-300 hover:text-accent hover:border-accent/40'
                      : 'border-slate-200 text-slate-600 hover:text-accent hover:border-accent/40'
                  }`}
                >
                  <Github size={16} />
                  GitHub
                </motion.a>
                <motion.a
                  href="https://linkedin.com/in/mallaprashanth"
                  target="_blank"
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.1, y: -2 }}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium bg-accent text-white hover:bg-highlight transition-colors"
                >
                  <Linkedin size={16} />
                  LinkedIn
                </motion.a>
              </div>
            </div>
          </motion.div>

          {/* Contact form */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.15 }}
            className={`lg:col-span-3 rounded-2xl border p-6 ${
              isDark
                ? 'bg-secondary/60 border-accent/20'
                : 'bg-white border-slate-200 shadow-lg shadow-slate-100'
            }`}
          >
            <h3 className={`font-heading font-bold text-xl mb-6 ${isDark ? 'text-white' : 'text-foreground'}`}>
              Send a Message
            </h3>

            {sent ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center py-12 gap-4"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200 }}
                  className="w-16 h-16 rounded-full bg-green-400/10 border-2 border-green-400 flex items-center justify-center"
                >
                  <Check size={28} className="text-green-400" />
                </motion.div>
                <p className={`font-heading font-semibold text-lg ${isDark ? 'text-white' : 'text-foreground'}`}>
                  Message Sent!
                </p>
                <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-muted'}`}>
                  I'll get back to you as soon as possible.
                </p>
              </motion.div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    { id: 'name', label: 'Full Name', placeholder: 'John Doe', type: 'text' },
                    { id: 'email', label: 'Email Address', placeholder: 'john@company.com', type: 'email' },
                  ].map(field => (
                    <div key={field.id}>
                      <label
                        htmlFor={field.id}
                        className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}
                      >
                        {field.label}
                      </label>
                      <input
                        id={field.id}
                        type={field.type}
                        required
                        placeholder={field.placeholder}
                        value={formState[field.id as keyof typeof formState]}
                        onChange={e => setFormState(p => ({ ...p, [field.id]: e.target.value }))}
                        className={`w-full px-4 py-3 rounded-xl border text-sm transition-all outline-none focus:border-accent focus:ring-2 focus:ring-accent/10 ${
                          isDark
                            ? 'bg-primary/60 border-white/10 text-white placeholder-slate-500'
                            : 'bg-surface border-slate-200 text-foreground placeholder-slate-400'
                        }`}
                      />
                    </div>
                  ))}
                </div>

                <div>
                  <label htmlFor="subject" className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                    Subject
                  </label>
                  <input
                    id="subject"
                    type="text"
                    required
                    placeholder="Internship opportunity / Project collaboration"
                    value={formState.subject}
                    onChange={e => setFormState(p => ({ ...p, subject: e.target.value }))}
                    className={`w-full px-4 py-3 rounded-xl border text-sm transition-all outline-none focus:border-accent focus:ring-2 focus:ring-accent/10 ${
                      isDark
                        ? 'bg-primary/60 border-white/10 text-white placeholder-slate-500'
                        : 'bg-surface border-slate-200 text-foreground placeholder-slate-400'
                    }`}
                  />
                </div>

                <div>
                  <label htmlFor="message" className={`block text-sm font-medium mb-1.5 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                    Message
                  </label>
                  <textarea
                    id="message"
                    required
                    rows={5}
                    placeholder="Tell me about the opportunity or project..."
                    value={formState.message}
                    onChange={e => setFormState(p => ({ ...p, message: e.target.value }))}
                    className={`w-full px-4 py-3 rounded-xl border text-sm transition-all outline-none focus:border-accent focus:ring-2 focus:ring-accent/10 resize-none ${
                      isDark
                        ? 'bg-primary/60 border-white/10 text-white placeholder-slate-500'
                        : 'bg-surface border-slate-200 text-foreground placeholder-slate-400'
                    }`}
                  />
                </div>

                <motion.button
                  type="submit"
                  disabled={sending}
                  whileHover={sending ? {} : { scale: 1.02 }}
                  whileTap={sending ? {} : { scale: 0.98 }}
                  className={`w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm transition-all ${
                    sending
                      ? 'bg-accent/50 text-white cursor-not-allowed'
                      : 'bg-accent hover:bg-highlight text-white shadow-lg shadow-accent/20'
                  }`}
                >
                  {sending ? (
                    <>
                      <motion.div
                        className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Send Message
                    </>
                  )}
                </motion.button>
              </form>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
