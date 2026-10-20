export default function ThemeToggle({ theme, onToggle }) {
  return <button type="button" onClick={onToggle}
    className="field rounded-lg px-3 py-2 text-sm font-medium"
    aria-label={theme === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro'}>
    {theme === 'dark' ? '☀️ Modo claro' : '🌙 Modo oscuro'}
  </button>
}
