import type { GlobalThemeOverrides } from 'naive-ui'

export const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#14b8a6',
    primaryColorHover: '#0d9488',
    primaryColorPressed: '#0f766e',
    primaryColorSuppl: '#14b8a6',
    borderRadius: '10px',
    bodyColor: '#f8fafc',
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
  },
}

export const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#2dd4bf',
    primaryColorHover: '#5eead4',
    primaryColorPressed: '#14b8a6',
    primaryColorSuppl: '#2dd4bf',
    borderRadius: '10px',
    bodyColor: '#0f172a',
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
  },
}
