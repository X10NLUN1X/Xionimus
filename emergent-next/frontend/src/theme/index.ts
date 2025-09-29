import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

// Color mode config
const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
}

// Black & Gold color palette
const colors = {
  primary: {
    50: '#FFFEF7',   // Very light gold tint
    100: '#FFF8DC',  // Light cream gold
    200: '#FFE135',  // Light gold
    300: '#FFD700',  // Classic gold
    400: '#FFC107',  // Rich gold
    500: '#FFB300',  // Main primary gold
    600: '#FF8F00',  // Dark gold
    700: '#F57C00',  // Darker gold
    800: '#E65100',  // Deep gold
    900: '#BF360C',  // Darkest gold/bronze
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

// Component styles
const components = {
  Button: {
    defaultProps: {
      colorScheme: 'primary',
    },
    variants: {
      solid: {
        bg: 'primary.500',
        color: 'white',
        _hover: {
          bg: 'primary.600',
          transform: 'translateY(-1px)',
          shadow: 'lg',
        },
        _active: {
          bg: 'primary.700',
          transform: 'translateY(0)',
        },
      },
      ghost: {
        _hover: {
          bg: 'primary.50',
          _dark: {
            bg: 'primary.900',
          },
        },
      },
    },
  },
  Card: {
    baseStyle: {
      container: {
        bg: 'white',
        _dark: {
          bg: 'gray.800',
        },
        shadow: 'sm',
        _hover: {
          shadow: 'md',
        },
        transition: 'all 0.2s',
      },
    },
  },
  Input: {
    variants: {
      filled: {
        field: {
          bg: 'gray.50',
          _dark: {
            bg: 'gray.700',
          },
          _hover: {
            bg: 'gray.100',
            _dark: {
              bg: 'gray.600',
            },
          },
          _focus: {
            bg: 'white',
            _dark: {
              bg: 'gray.800',
            },
            borderColor: 'primary.500',
          },
        },
      },
    },
  },
}

// Global styles
const styles = {
  global: {
    body: {
      bg: 'gray.50',
      _dark: {
        bg: 'gray.900',
      },
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