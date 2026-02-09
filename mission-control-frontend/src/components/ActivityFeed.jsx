import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Commit,
  BugReport,
  CheckCircle,
  PersonAdd,
  Comment,
  MergeType,
} from '@mui/icons-material';

const activities = [
  {
    id: 1,
    type: 'commit',
    user: 'Alex Chen',
    avatar: 'A',
    action: 'pushed 3 commits to',
    target: 'RE: UNITE',
    time: '2 min ago',
    color: '#667eea',
  },
  {
    id: 2,
    type: 'deploy',
    user: 'System',
    avatar: 'S',
    action: 'deployed',
    target: 'YouTube KOE v2.1.0',
    time: '5 min ago',
    color: '#4ade80',
  },
  {
    id: 3,
    type: 'bug',
    user: 'Sarah Kim',
    avatar: 'S',
    action: 'reported bug in',
    target: 'Trading module',
    time: '12 min ago',
    color: '#ff6b6b',
  },
  {
    id: 4,
    type: 'member',
    user: 'Mike Johnson',
    avatar: 'M',
    action: 'joined',
    target: 'ETHEREAL project',
    time: '25 min ago',
    color: '#f093fb',
  },
  {
    id: 5,
    type: 'merge',
    user: 'Lisa Wang',
    avatar: 'L',
    action: 'merged PR #234 in',
    target: 'Lovable Websites',
    time: '34 min ago',
    color: '#4ecdc4',
  },
  {
    id: 6,
    type: 'comment',
    user: 'David Park',
    avatar: 'D',
    action: 'commented on',
    target: 'Streaming API docs',
    time: '1 hour ago',
    color: '#a78bfa',
  },
];

const iconMap = {
  commit: Commit,
  deploy: CheckCircle,
  bug: BugReport,
  member: PersonAdd,
  merge: MergeType,
  comment: Comment,
};

function ActivityFeed() {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#e0e0ff' }}>
            Activity Feed
          </Typography>
          <Chip
            size="small"
            label="Live"
            sx={{
              height: 22,
              fontSize: '0.7rem',
              fontWeight: 600,
              backgroundColor: 'rgba(255, 107, 107, 0.15)',
              color: '#ff6b6b',
              border: '1px solid rgba(255, 107, 107, 0.3)',
              animation: 'pulse 2s infinite',
              '@keyframes pulse': {
                '0%': { opacity: 1 },
                '50%': { opacity: 0.7 },
                '100%': { opacity: 1 },
              },
            }}
          />
        </Box>

        <List sx={{ p: 0 }}>
          {activities.map((activity, index) => {
            const Icon = iconMap[activity.type];
            const isLast = index === activities.length - 1;

            return (
              <ListItem
                key={activity.id}
                sx={{
                  px: 0,
                  py: 1.5,
                  borderBottom: isLast ? 'none' : '1px solid rgba(102, 126, 234, 0.08)',
                }}
              >
                <ListItemAvatar>
                  <Avatar
                    sx={{
                      width: 40,
                      height: 40,
                      bgcolor: `${activity.color}20`,
                      color: activity.color,
                      fontWeight: 600,
                      fontSize: '0.9rem',
                    }}
                  >
                    {activity.avatar}
                  </Avatar>
                </ListItemAvatar>
                
                <ListItemText
                  primary={
                    <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap' }}>
                      <Typography component="span" variant="body2" sx={{ fontWeight: 600, color: '#e0e0ff' }}>
                        {activity.user}
                      </Typography>
                      <Typography component="span" variant="body2" sx={{ color: '#a0a0c0' }}>
                        {activity.action}
                      </Typography>
                      <Typography component="span" variant="body2" sx={{ fontWeight: 600, color: activity.color }}>
                        {activity.target}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                      <Icon sx={{ color: activity.color, fontSize: 14 }} />
                      <Typography variant="caption" sx={{ color: '#a0a0c0' }}>
                        {activity.time}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            );
          })}
        </List>
      </CardContent>
    </Card>
  );
}

export default ActivityFeed;
