import React from 'react';
import {
  AppBar,
  Toolbar,
  Box,
  Typography,
  Chip,
  IconButton,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  Memory,
  Token,
  Speed,
  Notifications,
  Search,
} from '@mui/icons-material';

function TopBar({ systemStats }) {
  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        background: 'linear-gradient(90deg, #1a1a2e 0%, #16162a 100%)',
        borderBottom: '1px solid rgba(102, 126, 234, 0.1)',
      }}
    >
      <Toolbar sx={{ px: 4, py: 1 }}>
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, color: '#e0e0ff' }}>
            Dashboard
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 3 }}>
            <StatChip
              icon={<Token sx={{ color: '#667eea', fontSize: 18 }} />}
              label="Tokens"
              value={systemStats.tokens.toLocaleString()}
              color="#667eea"
            />
            <StatChip
              icon={<Memory sx={{ color: '#4ade80', fontSize: 18 }} />}
              label="Memory"
              value={`${systemStats.memory}%`}
              color="#4ade80"
            />
            <StatChip
              icon={<Speed sx={{ color: '#f093fb', fontSize: 18 }} />}
              label="CPU"
              value={`${systemStats.cpu}%`}
              color="#f093fb"
            />
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton sx={{ color: '#a0a0c0', '&:hover': { color: '#667eea' } }}>
            <Search />
          </IconButton>
          
          <IconButton sx={{ color: '#a0a0c0', '&:hover': { color: '#667eea' } }}>
            <Notifications />
          </IconButton>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, ml: 2 }}>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#e0e0ff' }}>
                Commander
              </Typography>
              <Typography variant="caption" sx={{ color: '#667eea' }}>
                Admin
              </Typography>
            </Box>
            <Avatar
              sx={{
                width: 42,
                height: 42,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                fontWeight: 600,
              }}
            >
              C
            </Avatar>
          </Box>
        </Box>
      </Toolbar>
      
      <LinearProgress
        variant="determinate"
        value={systemStats.memory}
        sx={{
          height: 2,
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          '& .MuiLinearProgress-bar': {
            background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
          },
        }}
      />
    </AppBar>
  );
}

function StatChip({ icon, label, value, color }) {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        backgroundColor: 'rgba(102, 126, 234, 0.05)',
        border: '1px solid rgba(102, 126, 234, 0.1)',
        borderRadius: 3,
        px: 2,
        py: 1,
      }}
    >
      {icon}
      <Box>
        <Typography variant="caption" sx={{ color: '#a0a0c0', display: 'block', lineHeight: 1 }}>
          {label}
        </Typography>
        <Typography variant="body2" sx={{ color, fontWeight: 700, lineHeight: 1.2 }}>
          {value}
        </Typography>
      </Box>
    </Box>
  );
}

export default TopBar;
