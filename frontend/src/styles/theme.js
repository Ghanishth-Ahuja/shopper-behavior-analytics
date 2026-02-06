import { createTheme } from '@mui/material/styles';
import { CHART_COLORS } from '../utils/constants';

// Light theme
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: CHART_COLORS.PRIMARY,
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: CHART_COLORS.SECONDARY,
      light: '#f06292',
      dark: '#c2185b',
      contrastText: '#ffffff',
    },
    success: {
      main: CHART_COLORS.SUCCESS,
      light: '#4caf50',
      dark: '#2e7d32',
      contrastText: '#ffffff',
    },
    warning: {
      main: CHART_COLORS.WARNING,
      light: '#ffa726',
      dark: '#f57c00',
      contrastText: '#ffffff',
    },
    error: {
      main: CHART_COLORS.ERROR,
      light: '#ef5350',
      dark: '#c62828',
      contrastText: '#ffffff',
    },
    info: {
      main: CHART_COLORS.INFO,
      light: '#42a5f5',
      dark: '#1976d2',
      contrastText: '#ffffff',
    },
    grey: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: '#9e9e9e',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.125rem',
      fontWeight: 300,
      lineHeight: 1.167,
    },
    h2: {
      fontSize: '1.5rem',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: '1.25rem',
      fontWeight: 400,
      lineHeight: 1.167,
    },
    h4: {
      fontSize: '1.125rem',
      fontWeight: 500,
      lineHeight: 1.235,
    },
    h5: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.334,
    },
    h6: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.6,
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.75,
    },
    subtitle2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.57,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.43,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.75,
      textTransform: 'none',
    },
    caption: {
      fontSize: '0.75rem',
      fontWeight: 400,
      lineHeight: 1.66,
    },
    overline: {
      fontSize: '0.75rem',
      fontWeight: 400,
      lineHeight: 2.66,
      textTransform: 'uppercase',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#f1f1f1',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#c1c1c1',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: '#a8a8a8',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
          padding: '8px 16px',
        },
        contained: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
        elevation2: {
          boxShadow: '0 4px 8px rgba(0,0,0,0.12)',
        },
        elevation3: {
          boxShadow: '0 6px 12px rgba(0,0,0,0.15)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          fontWeight: 500,
        },
        outlined: {
          border: '1px solid rgba(0, 0, 0, 0.23)',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          backgroundColor: '#fafafa',
          fontWeight: 600,
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        hover: {
          backgroundColor: 'rgba(0, 0, 0, 0.04)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          color: 'rgba(0, 0, 0, 0.87)',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiToolbar: {
      styleOverrides: {
        root: {
          minHeight: 64,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid rgba(0, 0, 0, 0.12)',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 4px',
          '&.Mui-selected': {
            backgroundColor: 'rgba(25, 118, 210, 0.08)',
            '&:hover': {
              backgroundColor: 'rgba(25, 118, 210, 0.12)',
            },
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '0.875rem',
          minHeight: 48,
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 6,
        },
        bar: {
          borderRadius: 4,
        },
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },
});

// Dark theme
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: CHART_COLORS.PRIMARY,
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: CHART_COLORS.SECONDARY,
      light: '#f06292',
      dark: '#c2185b',
      contrastText: '#ffffff',
    },
    success: {
      main: CHART_COLORS.SUCCESS,
      light: '#4caf50',
      dark: '#2e7d32',
      contrastText: '#ffffff',
    },
    warning: {
      main: CHART_COLORS.WARNING,
      light: '#ffa726',
      dark: '#f57c00',
      contrastText: '#000000',
    },
    error: {
      main: CHART_COLORS.ERROR,
      light: '#ef5350',
      dark: '#c62828',
      contrastText: '#ffffff',
    },
    info: {
      main: CHART_COLORS.INFO,
      light: '#42a5f5',
      dark: '#1976d2',
      contrastText: '#ffffff',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
      disabled: 'rgba(255, 255, 255, 0.5)',
    },
  },
  typography: lightTheme.typography,
  components: lightTheme.components,
  breakpoints: lightTheme.breakpoints,
});

// Custom theme for charts
export const chartTheme = {
  colors: {
    primary: CHART_COLORS.PRIMARY,
    secondary: CHART_COLORS.SECONDARY,
    success: CHART_COLORS.SUCCESS,
    warning: CHART_COLORS.WARNING,
    error: CHART_COLORS.ERROR,
    info: CHART_COLORS.INFO,
    grey: CHART_COLORS.GREY,
    positive: CHART_COLORS.POSITIVE,
    negative: CHART_COLORS.NEGATIVE,
    neutral: CHART_COLORS.NEUTRAL,
  },
  gradients: CHART_COLORS.GRADIENTS,
  segments: [
    '#0088FE',
    '#00C49F',
    '#FFBB28',
    '#FF8042',
    '#8884D8',
    '#82CA9D',
    '#FFC658',
    '#FF7C7C',
    '#8DD1E1',
    '#D084D0',
  ],
};

export default lightTheme;
