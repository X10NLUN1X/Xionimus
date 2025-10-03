// Xionimus Color Theme
export const colors = {
  // Primary accent color (darker, less harsh)
  accent: {
    light: '#0088cc',  // Dunkleres Cyan (vorher: #00d4ff)
    main: '#0077bb',   // Noch dunkler für besseren Kontrast
    dark: '#006699',   // Dunkelste Variante
  },
  
  // Gradient colors
  gradient: {
    start: '#0088cc',  // Dunkleres Cyan (vorher: #00d4ff)
    end: '#0066aa',    // Dunkleres Blau (vorher: #0094ff)
  },
  
  // Original für Referenz (nicht verwenden)
  // old: { light: '#00d4ff', main: '#0094ff' }
}

export const getAccentColor = (colorMode: 'light' | 'dark') => {
  return colorMode === 'light' ? colors.accent.main : colors.accent.light
}

export const getGradient = () => {
  return `linear-gradient(135deg, ${colors.gradient.start}, ${colors.gradient.end})`
}
