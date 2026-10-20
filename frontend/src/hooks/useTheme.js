import { useEffect, useState } from 'react'
const KEY = 'practica-1:theme'

function preferredTheme() {
  try {
    const stored = window.localStorage.getItem(KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch { /* almacenamiento puede estar deshabilitado */ }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function useTheme() {
  const [theme, setTheme] = useState(preferredTheme)
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    try { window.localStorage.setItem(KEY, theme) } catch { /* tema visual igualmente funciona */ }
  }, [theme])
  const toggleTheme = () => setTheme(current => current === 'dark' ? 'light' : 'dark')
  return { theme, toggleTheme }
}
