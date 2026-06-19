export interface NavItem {
  label: string;
  href: string;
}

export interface Skill {
  name: string;
  level: number;
  icon: string;
}

export interface SkillCategory {
  title: string;
  icon: string;
  color: string;
  skills: Skill[];
}

export interface Project {
  id: string;
  title: string;
  badge?: string;
  description: string;
  highlights: string[];
  tags: string[];
  metrics: { label: string; value: string }[];
  github?: string;
  featured?: boolean;
  color: string;
}

export interface Experience {
  role: string;
  company: string;
  unit: string;
  duration: string;
  responsibilities: string[];
}

export interface Certification {
  title: string;
  issuer: string;
  year: string;
  icon: string;
}

export interface Achievement {
  title: string;
  description: string;
  icon: string;
  color: string;
}

export interface ThemeContextType {
  isDark: boolean;
  toggleTheme: () => void;
}
