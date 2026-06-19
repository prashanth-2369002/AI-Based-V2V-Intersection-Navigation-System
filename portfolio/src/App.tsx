import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import About from './components/About'
import TechnicalExpertise from './components/TechnicalExpertise'
import Projects from './components/Projects'
import Experience from './components/Experience'
import Certifications from './components/Certifications'
import Achievements from './components/Achievements'
import Contact from './components/Contact'
import Footer from './components/Footer'

function App() {
  const [isDark, setIsDark] = useState(true)

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  const toggleTheme = () => setIsDark(prev => !prev)

  return (
    <div className={`min-h-screen font-body transition-colors duration-300 ${isDark ? 'bg-primary text-white' : 'bg-surface text-foreground'}`}>
      <Navbar isDark={isDark} toggleTheme={toggleTheme} />
      <main>
        <Hero isDark={isDark} />
        <About isDark={isDark} />
        <TechnicalExpertise isDark={isDark} />
        <Projects isDark={isDark} />
        <Experience isDark={isDark} />
        <Certifications isDark={isDark} />
        <Achievements isDark={isDark} />
        <Contact isDark={isDark} />
      </main>
      <Footer isDark={isDark} />
    </div>
  )
}

export default App
