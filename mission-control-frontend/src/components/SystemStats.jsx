import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  LinearProgress,
} from '@mui/material';
import {
  Storage,
  CloudQueue,
  Speed,
  Security,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';

const stats = [
  {
    id: 1,
    title: 'Server Uptime',
    value: '99.98%',
    subtitle: 'Last 30 days',
    icon: Storage,
    color: '#4ade80',
    trend: 'up',
    trendValue: '+0.02%',
  },
  {
    id: 2,
    title: 'API Requests',
    value: '2.4M',
    subtitle: 'Today',
    icon: CloudQueue,
    color: '#667eea',
    trend: 'up',
    trendValue: '+12.5%',
  },
  {
    id: 3,
    title: 'Avg Response',
    value: '45ms',
    subtitle: 'Global avg',
    icon: Speed,
    color: '#f093fb',
    trend: 'down',
    trendValue: '-8ms',
  },
  {
    id: 4,
    title: 'Security Score',
    value: 'A+',
    subtitle: 'All systems',
    icon: Security,
    color: '#4ecdc4',
    trend: 'up',
    trendValue: '+5pts',
  },
];

const systemMetrics = [
  { label: 'Database', value: 72, color: '#667eea' },
  { label: 'Cache', value: 45, color: '#4ade80' },
  { label: 'Queue', value: 28, color: '#f093fb' },
  { label: 'Storage', value: 61, color: '#4ecdc4' },
];

function SystemStats() {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#e0e0ff', mb: 3 }}>
          System Health
        </Typography>

        <Grid container spacing={2} sx={{ mb: 4 }}>
          {stats.map((stat) => {
            const Icon = stat.icon;
            const TrendIcon = stat.trend === 'up' ? TrendingUp : TrendingDown;

            return (
              <Grid item xs={6} key={stat.id}>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 3,
                    backgroundColor: 'rgba(102, 126, 234, 0.05)',
                    border: '1px solid rgba(102, 126, 234, 0.1)',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Icon sx={{ color: stat.color, fontSize: 28 }} />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <TrendIcon sx={{ color: stat.color, fontSize: 14 }} />
                      <Typography variant="caption" sx={{ color: stat.color, fontWeight: 600 }}>
                        {stat.trendValue}
                      </Typography>
                    </Box>
                  </Box>

                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#e0e0ff', mb: 0.5 }}>
                    {stat.value}
                  </Typography>

                  <Typography variant="caption" sx={{ color: '#a0a0c0', display: 'block' }}>
                    {stat.title}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#667eea' }}>
                    {stat.subtitle}
                  </Typography>
                </Box>
              </Grid>
            );
          })}
        </Grid>

        <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#e0e0ff', mb: 2 }}>
          Resource Usage
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {systemMetrics.map((metric) => (
            <Box key={metric.label}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" sx={{ color: '#a0a0c0' }}>
                  {metric.label}
                </Typography>
                <Typography variant="caption" sx={{ color: metric.color, fontWeight: 600 }}>
                  {metric.value}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={metric.value}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: 'rgba(102, 126, 234, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: metric.color,
                    borderRadius: 3,
                  },
                }}
              />
            </Box>
          ))}
        </Box>

        <Box
          sx={{
            mt: 3,
            p: 2,
            borderRadius: 3,
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
            border: '1px solid rgba(102, 126, 234, 0.2)',
          }}
        >
          <Typography variant="body2" sx={{ color: '#e0e0ff', fontWeight: 600, mb: 0.5 }}>
            All Systems Operational
          </Typography>
          <Typography variant="caption" sx={{ color: '#a0a0c0' }}>
            Last checked: Just now
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default SystemStats;
