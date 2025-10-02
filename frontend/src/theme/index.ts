import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

// Color mode config
const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
}

// Modern Dark Blue & Cyan color palette (Artifi style)
const colors = {
  primary: {
    50: '#E0F7FA',   // Very light cyan tint
    100: '#B2EBF2',  // Light cyan
    200: '#80DEEA',  // Soft cyan
    300: '#4DD0E1',  // Bright cyan
    400: '#26C6DA',  // Rich cyan
    500: '#00d4ff',  // Main primary cyan (Xionimus signature)
    600: '#00B8D4',  // Deep cyan
    700: '#0097A7',  // Dark cyan
    800: '#00838F',  // Very dark cyan
    900: '#006064',  // Deepest cyan
  },
  accent: {
    50: '#FAFAFA',   // Almost white
    100: '#F5F5F5',  // Very light gray
    200: '#EEEEEE',  // Light gray
    300: '#E0E0E0',  // Medium light gray
    400: '#BDBDBD',  // Medium gray
    500: '#9E9E9E',  // Main accent gray
    600: '#757575',  // Dark gray
    700: '#616161',  // Darker gray
    800: '#424242',  // Very dark gray
    900: '#212121',  // Almost black
  },
  success: {
    50: '#E8F5E8',
    100: '#C8E6C9',
    200: '#A5D6A7',
    300: '#81C784',
    400: '#66BB6A',
    500: '#4CAF50', // Main success
    600: '#43A047',
    700: '#388E3C',
    800: '#2E7D32',
    900: '#1B5E20',
  },
  warning: {
    50: '#FFF8E1',
    100: '#FFECB3',
    200: '#FFE082',
    300: '#FFD54F',
    400: '#FFCA28',
    500: '#FFC107', // Main warning
    600: '#FFB300',
    700: '#FFA000',
    800: '#FF8F00',
    900: '#FF6F00',
  },
  error: {
    50: '#FFEBEE',
    100: '#FFCDD2',
    200: '#EF9A9A',
    300: '#E57373',
    400: '#EF5350',
    500: '#F44336', // Main error
    600: '#E53935',
    700: '#D32F2F',
    800: '#C62828',
    900: '#B71C1C',
  },
}

// Component styles - Dark Blue & Cyan Theme
const components = {
  Button: {
    defaultProps: {
      colorScheme: 'primary',
    },
    variants: {
      solid: {
        bg: 'linear-gradient(135deg, #00d4ff, #0094ff)',  // Cyan gradient
        color: '#FFFFFF',       // White text on cyan
        fontWeight: 'bold',
        _hover: {
          bg: 'linear-gradient(135deg, #0094ff, #00d4ff)',
          transform: 'translateY(-1px)',
          shadow: '0 4px 20px rgba(0, 212, 255, 0.6)',
        },
        _active: {
          bg: 'primary.600',
          transform: 'translateY(0)',
        },
      },
      ghost: {
        color: 'primary.500',   // Cyan text
        _hover: {
          bg: 'rgba(0, 212, 255, 0.1)',
          color: 'primary.400',
        },
      },
      outline: {
        borderColor: 'primary.500',
        color: 'primary.500',
        _hover: {
          bg: 'rgba(0, 212, 255, 0.1)',
          color: 'primary.400',
        },
      },
    },
  },
  Card: {
    baseStyle: {
      container: {
        bg: '#111111',          // Very dark gray
        borderColor: '#333333', // Dark border
        borderWidth: '1px',
        shadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
        _hover: {
          shadow: '0 8px 25px rgba(0, 212, 255, 0.15)',
          borderColor: 'primary.500',
        },
        transition: 'all 0.3s ease',
      },
    },
  },
  Input: {
    variants: {
      filled: {
        field: {
          bg: '#222222',        // Dark background
          color: '#FFFFFF',     // White text
          borderColor: '#444444',
          _hover: {
            bg: '#333333',
            borderColor: '#555555',
          },
          _focus: {
            bg: '#111111',
            borderColor: 'primary.500',
            boxShadow: '0 0 0 1px #00d4ff',
          },
        },
      },
      outline: {
        field: {
          borderColor: '#444444',
          color: '#FFFFFF',
          _hover: {
            borderColor: '#666666',
          },
          _focus: {
            borderColor: 'primary.500',
            boxShadow: '0 0 0 1px #FFB300',
          },
        },
      },
    },
  },
  Textarea: {
    variants: {
      filled: {
        bg: '#222222',
        color: '#FFFFFF',
        borderColor: '#444444',
        _hover: {
          bg: '#333333',
          borderColor: '#555555',
        },
        _focus: {
          bg: '#111111',
          borderColor: 'primary.500',
          boxShadow: '0 0 0 1px #FFB300',
        },
      },
    },
  },
  Menu: {
    baseStyle: {
      list: {
        bg: '#111111',
        borderColor: '#333333',
        shadow: '0 8px 25px rgba(0, 0, 0, 0.5)',
      },
      item: {
        bg: 'transparent',
        color: '#FFFFFF',
        _hover: {
          bg: 'rgba(0, 212, 255, 0.1)',
          color: 'primary.400',
        },
        _focus: {
          bg: 'rgba(0, 212, 255, 0.1)',
          color: 'primary.400',
        },
      },
    },
  },
  Modal: {
    baseStyle: {
      dialog: {
        bg: '#111111',
        borderColor: '#333333',
        borderWidth: '1px',
      },
      header: {
        color: 'primary.500',
        fontWeight: 'bold',
      },
      body: {
        color: '#FFFFFF',
      },
    },
  },
}

// Global styles - Dark Blue & Cyan Theme mit verbesserter Typography
const styles = {
  global: {
    body: {
      bg: '#0A0A0A',      // Rich black background
      color: '#E8E8E8',   // Soft white for better readability
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif",
      fontSize: '16px',   // Base font size
      lineHeight: '1.7',  // Better line height for readability
      letterSpacing: '0.01em',
      WebkitFontSmoothing: 'antialiased',
      MozOsxFontSmoothing: 'grayscale',
    },
      color: '#FFFFFF',   // Pure white text
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      lineHeight: '1.6',
      _dark: {
        bg: '#000000',    // Absolute black for dark mode
        color: '#FFFFFF',
      },
    },
    '*::placeholder': {
      color: 'rgba(255, 255, 255, 0.4)',
    },
    '*, *::before, &::after': {
      borderColor: 'rgba(0, 212, 255, 0.2)',
    },
    // Scrollbar styling
    '::-webkit-scrollbar': {
      width: '8px',
    },
    '::-webkit-scrollbar-track': {
      bg: 'rgba(17, 17, 17, 0.8)',
    },
    '::-webkit-scrollbar-thumb': {
      bg: 'rgba(0, 212, 255, 0.3)',
      borderRadius: '4px',
      _hover: {
        bg: 'rgba(0, 212, 255, 0.5)',
      },
    },
    // Selection styling
    '::selection': {
      bg: 'rgba(0, 212, 255, 0.3)',
      color: '#FFFFFF',
    },
  },
}

// Fonts
const fonts = {
  heading: `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"`,
  body: `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"`,
  mono: `'JetBrains Mono', SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace`,
}

const theme = extendTheme({
  config,
  colors,
  components,
  styles,
  fonts,
  space: {
    px: '1px',
    0.5: '0.125rem',
    1: '0.25rem',
    1.5: '0.375rem',
    2: '0.5rem',
    2.5: '0.625rem',
    3: '0.75rem',
    3.5: '0.875rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    7: '1.75rem',
    8: '2rem',
    9: '2.25rem',
    10: '2.5rem',
    12: '3rem',
    14: '3.5rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
    28: '7rem',
    32: '8rem',
    36: '9rem',
    40: '10rem',
    44: '11rem',
    48: '12rem',
    52: '13rem',
    56: '14rem',
    60: '15rem',
    64: '16rem',
    72: '18rem',
    80: '20rem',
    96: '24rem',
  },
})

export default theme