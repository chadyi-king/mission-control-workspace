import React from 'react';
import {
  Box,
  Grid,
  Typography,
} from '@mui/material';
import { ProjectCard, projectData } from './ProjectCard';
import ActivityFeed from './ActivityFeed';
import SystemStats from './SystemStats';

function Dashboard() {
  return (
    <Box
      sx={{
        flexGrow: 1,
        p: 4,
        background: 'linear-gradient(135deg, #0f0f1e 0%, #16162a 100%)',
        overflowY: 'auto',
        '&::-webkit-scrollbar': {
          width: 8,
        },
        '&::-webkit-scrollbar-track': {
          background: 'rgba(102, 126, 234, 0.05)',
        },
        '&::-webkit-scrollbar-thumb': {
          background: 'rgba(102, 126, 234, 0.2)',
          borderRadius: 4,
        },
      }}
    >
      <Typography variant="h4" sx={{ fontWeight: 700, color: '#e0e0ff', mb: 1 }}>
        Welcome back, Commander
      </Typography>
      <Typography variant="body1" sx={{ color: '#a0a0c0', mb: 4 }}>
        Here's what's happening across your missions today.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#e0e0ff', mb: 2 }}>
            Active Projects
          </Typography>
          
          <Grid container spacing={3}>
            {projectData.map((project) => (
              <Grid item xs={12} md={6} key={project.id}>
                <ProjectCard project={project} />
              </Grid>
            ))}
          </Grid>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Box sx={{ height: 400 }}>
              <ActivityFeed />
            </Box>
            
            <Box sx={{ height: 420 }}>
              <SystemStats />
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
