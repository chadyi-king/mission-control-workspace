import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  IconButton,
} from '@mui/material';
import {
  MoreVert,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';

const projectData = [
  {
    id: 1,
    name: 'RE: UNITE',
    description: 'AI-powered collaboration platform',
    status: 'active',
    progress: 78,
    tasks: { completed: 156, total: 200 },
    team: 8,
    trend: 'up',
    trendValue: '+12%',
    color: '#667eea',
    lastUpdate: '2 min ago',
  },
  {
    id: 2,
    name: 'Lovable Websites',
    description: 'No-code website builder',
    status: 'active',
    progress: 92,
    tasks: { completed: 89, total: 97 },
    team: 5,
    trend: 'up',
    trendValue: '+8%',
    color: '#f093fb',
    lastUpdate: '15 min ago',
  },
  {
    id: 3,
    name: 'YouTube KOE',
    description: 'Content creation automation',
    status: 'live',
    progress: 100,
    tasks: { completed: 234, total: 234 },
    team: 12,
    trend: 'up',
    trendValue: '+24%',
    color: '#ff6b6b',
    lastUpdate: 'Just now',
  },
  {
    id: 4,
    name: 'Streaming',
    description: 'Live stream management system',
    status: 'offline',
    progress: 45,
    tasks: { completed: 34, total: 75 },
    team: 6,
    trend: 'down',
    trendValue: '-3%',
    color: '#4ecdc4',
    lastUpdate: '1 hour ago',
  },
  {
    id: 5,
    name: 'ETHEREAL',
    description: '3D virtual world engine',
    status: 'active',
    progress: 63,
    tasks: { completed: 128, total: 203 },
    team: 15,
    trend: 'up',
    trendValue: '+5%',
    color: '#a78bfa',
    lastUpdate: '30 min ago',
  },
  {
    id: 6,
    name: 'Trading',
    description: 'Algorithmic trading bot',
    status: 'active',
    progress: 85,
    tasks: { completed: 67, total: 79 },
    team: 4,
    trend: 'up',
    trendValue: '+18%',
    color: '#4ade80',
    lastUpdate: '5 min ago',
  },
];

function ProjectCard({ project }) {
  const TrendIcon = project.trend === 'up' ? TrendingUp : project.trend === 'down' ? TrendingDown : TrendingFlat;
  const trendColor = project.trend === 'up' ? '#4ade80' : project.trend === 'down' ? '#ff6b6b' : '#a0a0c0';

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 12px 40px -12px ${project.color}30`,
          borderColor: `${project.color}40`,
        },
      }}
    >
      <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#e0e0ff', mb: 0.5 }}>
              {project.name}
            </Typography>
            <Typography variant="body2" sx={{ color: '#a0a0c0' }}>
              {project.description}
            </Typography>
          </Box>
          <IconButton size="small" sx={{ color: '#a0a0c0' }}>
            <MoreVert />
          </IconButton>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
          <Chip
            size="small"
            label={project.status}
            sx={{
              height: 24,
              fontSize: '0.7rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              backgroundColor:
                project.status === 'active'
                  ? 'rgba(74, 222, 128, 0.15)'
                  : project.status === 'live'
                  ? 'rgba(255, 107, 107, 0.15)'
                  : 'rgba(160, 160, 192, 0.15)',
              color:
                project.status === 'active'
                  ? '#4ade80'
                  : project.status === 'live'
                  ? '#ff6b6b'
                  : '#a0a0c0',
              border: `1px solid ${
                project.status === 'active'
                  ? 'rgba(74, 222, 128, 0.3)'
                  : project.status === 'live'
                  ? 'rgba(255, 107, 107, 0.3)'
                  : 'rgba(160, 160, 192, 0.3)'
              }`,
            }}
          />
          <Chip
            size="small"
            icon={<TrendIcon sx={{ color: trendColor, fontSize: 16 }} />}
            label={project.trendValue}
            sx={{
              height: 24,
              fontSize: '0.7rem',
              fontWeight: 600,
              backgroundColor: `${trendColor}15`,
              color: trendColor,
              border: `1px solid ${trendColor}30`,
            }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="caption" sx={{ color: '#a0a0c0' }}>
              Progress
            </Typography>
            <Typography variant="caption" sx={{ color: '#e0e0ff', fontWeight: 600 }}>
              {project.progress}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={project.progress}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'rgba(102, 126, 234, 0.1)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: project.color,
                borderRadius: 3,
              },
            }}
          />
        </Box>

        <Box
          sx={{
            mt: 'auto',
            pt: 2,
            borderTop: '1px solid rgba(102, 126, 234, 0.1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Box>
            <Typography variant="caption" sx={{ color: '#a0a0c0', display: 'block' }}>
              {project.tasks.completed}/{project.tasks.total} tasks
            </Typography>
            <Typography variant="caption" sx={{ color: '#667eea' }}>
              {project.team} team members
            </Typography>
          </Box>
          <Typography variant="caption" sx={{ color: '#a0a0c0' }}>
            {project.lastUpdate}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export { ProjectCard, projectData };
export default ProjectCard;
