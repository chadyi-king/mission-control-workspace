import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import Dashboard from './components/Dashboard';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#0f0f1e',
      paper: '#1a1a2e',
    },
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
    text: {
      primary: '#e0e0ff',
      secondary: '#a0a0c0',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(145deg, #1a1a2e 0%, #16162a 100%)',
          border: '1px solid rgba(102, 126, 234, 0.15)',
          borderRadius: 16,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

function App() {
  const [systemStats, setSystemStats] = useState({
    tokens: 0,
    memory: 0,
    cpu: 0,
  });

  useEffect(() => {
    // Simulate live system stats updates
    const interval = setInterval(() => {
      setSystemStats({
        tokens: Math.floor(Math.random() * 50000) + 10000,
        memory: Math.floor(Math.random() * 30) + 40,
        cpu: Math.floor(Math.random() * 40) + 20,
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        <Sidebar />
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <TopBar systemStats={systemStats} />
          <Dashboard />
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
