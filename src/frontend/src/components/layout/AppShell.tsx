/**
 * AppShell Component
 * Main application layout with responsive navigation
 * Handles mobile drawer and desktop sidebar
 */

import React, { useState } from 'react';
import {
  Box,
  CssBaseline,
  useTheme,
  useMediaQuery,
} from '@mui/material';

import Header from './Header';
import Sidebar from './Sidebar';
import { logger } from '@utils/logger';

interface AppShellProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 280;

const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileDrawerOpen(!mobileDrawerOpen);
    logger.userInteraction('AppShell', 'drawer_toggle', {
      isOpen: !mobileDrawerOpen,
      isMobile
    });
  };

  const handleDrawerClose = () => {
    setMobileDrawerOpen(false);
    logger.userInteraction('AppShell', 'drawer_close', { isMobile });
  };

  // Log layout render
  React.useEffect(() => {
    logger.debug('AppShell rendered', {
      component: 'AppShell',
      action: 'layout_rendered',
      metadata: {
        screenSize: isMobile ? 'mobile' : 'desktop',
        drawerWidth: DRAWER_WIDTH
      }
    });
  }, [isMobile]);

  return (
    <Box sx={{ display: 'flex' }} data-testid="app-shell">
      <CssBaseline />
      
      {/* Header */}
      <Header 
        drawerWidth={DRAWER_WIDTH}
        onDrawerToggle={handleDrawerToggle}
        isMobile={isMobile}
      />

      {/* Sidebar Navigation */}
      <Sidebar
        drawerWidth={DRAWER_WIDTH}
        mobileOpen={mobileDrawerOpen}
        onDrawerClose={handleDrawerClose}
        isMobile={isMobile}
      />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          marginLeft: isMobile ? 0 : 0, // Sidebar handles its own positioning
          marginTop: '64px', // Account for header height
          backgroundColor: theme.palette.background.default,
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        {/* Content with proper spacing */}
        <Box
          sx={{
            padding: theme.spacing(2),
            [theme.breakpoints.up('sm')]: {
              padding: theme.spacing(3),
            },
            [theme.breakpoints.up('md')]: {
              marginLeft: isMobile ? 0 : `${DRAWER_WIDTH}px`,
            },
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default AppShell;