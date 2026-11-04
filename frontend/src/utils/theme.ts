export type Theme = 'light' | 'dark'

const storageKey = 'hhl-erp-theme'

export function readTheme(): Theme {
  try {
    return localStorage.getItem(storageKey) === 'dark' ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

export function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark')
  document.documentElement.style.colorScheme = theme
}

export function saveTheme(theme: Theme): boolean {
  applyTheme(theme)
  try {
    localStorage.setItem(storageKey, theme)
    return true
  } catch {
    return false
  }
}
