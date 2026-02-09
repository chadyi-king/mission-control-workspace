import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Chip,
} from '@mui/material';
import {
  RocketLaunch,
  Web,
  YouTube,
  LiveTv,
  AutoAwesome,
  ShowChart,
  Settings,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';

const drawerWidth = 260;

const projects = [
  { id: 1, name: 'RE: UNITE', icon: RocketLaunch, status: 'active', color: '#667eea' },
  { id: 2, name: 'Lovable Websites', icon: Web, status: 'active', color: '#f093fb' },
  { id: 3, name: 'YouTube KOE', icon: YouTube, status: 'live', color: '#ff6b6b' },
  { id: 4, name: 'Streaming', icon: LiveTv, status: 'offline', color: '#4ecdc4' },
  { id: 5, name: 'ETHEREAL', icon: AutoAwesome, status: 'active', color: '#a78bfa' },
  { id: 6, name: 'Trading', icon: ShowChart, status: 'active', color: '#4ade80' },
];

function Sidebar() {
  const [selected, setSelected] = useState(0);

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, #0f0f1e 0%, #16162a 100%)',
          borderRight: '1px solid rgba(102, 126, 234, 0.1)',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <Avatar
            sx={{
              bgcolor: 'transparent',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              width: 44,
              height: 44,
            }}
          >
            <RocketLaunch sx={{ color: 'white', fontSize: 24 }} />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.5px' }}>
              Mission Control
            </Typography>
            <Typography variant="caption" sx={{ color: '#667eea', fontWeight: 500 }}>
              v2.4.1
            </Typography>
          </Box>
        </Box>
      </Box>

      <Box sx={{ px: 2, pb: 2 }}>
        <ListItemButton
          selected={selected === 0}
          onClick={() => setSelected(0)}
          sx={{
            borderRadius: 3,
            mb: 1,
            backgroundColor: selected === 0 ? 'rgba(102, 126, 234, 0.15) !important' : 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(102, 126, 234, 0.08)',
            },
          }}
        >
          <ListItemIcon>
            <DashboardIcon sx={{ color: selected === 0 ? '#667eea' : '#a0a0c0' }} />
          </ListItemIcon>
          <ListItemText
            primary="Overview"
            sx={{
              '& .MuiListItemText-primary': {
                color: selected === 0 ? '#667eea' : '#e0e0ff',
                fontWeight: selected === 0 ? 600 : 400,
              },
            }}
          />
        </ListItemButton>
      </Box>

      <Typography
        variant="caption"
        sx={{ px: 3, pb: 1, color: '#667eea', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}
      >
        Projects
      </Typography>

      <List sx={{ px: 2 }}>
        {projects.map((project, index) => {
          const Icon = project.icon;
          return (
            <ListItem key={project.id} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={selected === index + 1}
                onClick={() => setSelected(index + 1)}
                sx={{
                  borderRadius: 3,
                  backgroundColor: selected === index + 1 ? 'rgba(102, 126, 234, 0.15) !important' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(102, 126, 234, 0.08)',
                  },
                }}
              >
                <ListItemIcon>
                  <Icon sx={{ color: selected === index + 1 ? project.color : '#a0a0c0', fontSize: 22 }} />
                </ListItemIcon>
                <ListItemText
                  primary={project.name}
                  sx={{
                    '& .MuiListItemText-primary': {
                      color: selected === index + 1 ? '#e0e0ff' : '#a0a0c0',
                      fontWeight: selected === index + 1 ? 600 : 400,
                      fontSize: '0.9rem',
                    },
                  }}
                />
                <Chip
                  size="small"
                  label={project.status}
                  sx={{
                    height: 20,
                    fontSize: '0.65rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    backgroundColor:
                      project.status === 'active'
                        ? 'rgba(74, 222, 128, 0.2)'
                        : project.status === 'live'
                        ? 'rgba(255, 107, 107, 0.2)'
                        : 'rgba(160, 160, 192, 0.2)',
                    color:
                      project.status === 'active'
                        ? '#4ade80'
                        : project.status === 'live'
                        ? '#ff6b6b'
                        : '#a0a0c0',
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Box sx={{ mt: 'auto', p: 2 }}>
        <ListItemButton
          sx={{
            borderRadius: 3,
            color: '#a0a0c0',
            '&:hover': {
              backgroundColor: 'rgba(102, 126, 234, 0.08)',
            },
          }}
        >
          <ListItemIcon>
            <Settings sx={{ color: '#a0a0c0' }} />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItemButton>
      </Box>
    </Drawer>
  );
}

export default Sidebar;
