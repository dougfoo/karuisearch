/**
 * Sidebar Component
 * Navigation sidebar with property filters and main navigation
 * Responsive design for mobile drawer and desktop permanent sidebar
 */

import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Box,
  Collapse,
  useTheme,
  Badge,
} from '@mui/material';
import {
  HomeIcon,
  CalendarTodayIcon,
  ViewListIcon,
  TrendingUpIcon,
  LocationOnIcon,
  FilterListIcon,
  ExpandLessIcon,
  ExpandMoreIcon,
  FavoriteIcon,
  HistoryIcon,
  SettingsIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

import { logger } from '@utils/logger';

interface SidebarProps {
  drawerWidth: number;
  mobileOpen: boolean;
  onDrawerClose: () => void;
  isMobile: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  drawerWidth,
  mobileOpen,
  onDrawerClose,
  isMobile,
}) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [filtersOpen, setFiltersOpen] = React.useState(false);

  // Navigation items
  const mainNavItems = [
    {
      text: t('navigation.home'),
      icon: <HomeIcon />,
      path: '/',
      key: 'home',
    },
    {
      text: t('navigation.weeklyReport'),
      icon: <CalendarTodayIcon />,
      path: '/weekly',
      key: 'weekly',
      badge: 3, // Example: 3 new properties
    },
    {
      text: t('navigation.allListings'),
      icon: <ViewListIcon />,
      path: '/listings',
      key: 'listings',
    },
    {
      text: t('navigation.priceAnalysis'),
      icon: <TrendingUpIcon />,
      path: '/analysis',
      key: 'analysis',
    },
  ];

  const secondaryNavItems = [
    {
      text: t('navigation.favorites'),
      icon: <FavoriteIcon />,
      path: '/favorites',
      key: 'favorites',
    },
    {
      text: t('navigation.searchHistory'),
      icon: <HistoryIcon />,
      path: '/history',
      key: 'history',
    },
    {
      text: t('navigation.settings'),
      icon: <SettingsIcon />,
      path: '/settings',
      key: 'settings',
    },
  ];

  // Filter categories
  const filterCategories = [
    {
      text: t('filters.location'),
      icon: <LocationOnIcon />,
      key: 'location',
    },
    {
      text: t('filters.propertyType'),
      icon: <HomeIcon />,
      key: 'propertyType',
    },
    {
      text: t('filters.priceRange'),
      icon: <TrendingUpIcon />,
      key: 'priceRange',
    },
  ];

  const handleNavigate = (path: string, key: string) => {
    navigate(path);
    if (isMobile) {
      onDrawerClose();
    }
    logger.userInteraction('Sidebar', 'navigation_click', {
      destination: key,
      path,
      isMobile
    });
  };

  const handleFiltersToggle = () => {
    setFiltersOpen(!filtersOpen);
    logger.userInteraction('Sidebar', 'filters_toggle', {
      isOpen: !filtersOpen
    });
  };

  const handleFilterClick = (filterKey: string) => {
    logger.userInteraction('Sidebar', 'filter_click', {
      filterType: filterKey
    });
    // TODO: Implement filter functionality
  };

  const isCurrentPath = (path: string) => {
    return location.pathname === path;
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo/Brand Section */}
      <Box
        sx={{
          p: 2,
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: theme.palette.primary.main,
            textAlign: 'center',
          }}
        >
          軽井サーチ
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: theme.palette.text.secondary,
            textAlign: 'center',
            display: 'block',
            mt: 0.5,
          }}
        >
          {t('app.subtitle')}
        </Typography>
      </Box>

      {/* Main Navigation */}
      <List sx={{ flexGrow: 1, pt: 1 }}>
        {mainNavItems.map((item) => (
          <ListItem key={item.key} disablePadding>
            <ListItemButton
              onClick={() => handleNavigate(item.path, item.key)}
              selected={isCurrentPath(item.path)}
              sx={{
                mx: 1,
                borderRadius: 1,
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.light,
                  color: theme.palette.primary.contrastText,
                  '& .MuiListItemIcon-root': {
                    color: theme.palette.primary.contrastText,
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: isCurrentPath(item.path)
                    ? theme.palette.primary.contrastText
                    : theme.palette.text.secondary,
                }}
              >
                {item.badge ? (
                  <Badge badgeContent={item.badge} color="error">
                    {item.icon}
                  </Badge>
                ) : (
                  item.icon
                )}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.9rem',
                  fontWeight: isCurrentPath(item.path) ? 600 : 400,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}

        <Divider sx={{ my: 2, mx: 2 }} />

        {/* Quick Filters */}
        <ListItem disablePadding>
          <ListItemButton onClick={handleFiltersToggle} sx={{ mx: 1, borderRadius: 1 }}>
            <ListItemIcon>
              <FilterListIcon />
            </ListItemIcon>
            <ListItemText
              primary={t('navigation.quickFilters')}
              primaryTypographyProps={{ fontSize: '0.9rem' }}
            />
            {filtersOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItemButton>
        </ListItem>

        <Collapse in={filtersOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {filterCategories.map((filter) => (
              <ListItemButton
                key={filter.key}
                onClick={() => handleFilterClick(filter.key)}
                sx={{ pl: 4, mx: 1, borderRadius: 1 }}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  {filter.icon}
                </ListItemIcon>
                <ListItemText
                  primary={filter.text}
                  primaryTypographyProps={{ fontSize: '0.85rem' }}
                />
              </ListItemButton>
            ))}
          </List>
        </Collapse>

        <Divider sx={{ my: 2, mx: 2 }} />

        {/* Secondary Navigation */}
        {secondaryNavItems.map((item) => (
          <ListItem key={item.key} disablePadding>
            <ListItemButton
              onClick={() => handleNavigate(item.path, item.key)}
              selected={isCurrentPath(item.path)}
              sx={{
                mx: 1,
                borderRadius: 1,
                '&.Mui-selected': {
                  backgroundColor: theme.palette.action.selected,
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: isCurrentPath(item.path)
                    ? theme.palette.primary.main
                    : theme.palette.text.secondary,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.9rem',
                  fontWeight: isCurrentPath(item.path) ? 600 : 400,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Footer */}
      <Box
        sx={{
          p: 2,
          borderTop: `1px solid ${theme.palette.divider}`,
          textAlign: 'center',
        }}
      >
        <Typography variant="caption" color="text.secondary">
          {t('app.version')} v1.0.0
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box
      component="nav"
      sx={{ width: isMobile ? 0 : drawerWidth, flexShrink: 0 }}
      data-testid="sidebar"
    >
      {/* Mobile Drawer */}
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={onDrawerClose}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: theme.palette.background.paper,
            },
          }}
        >
          {drawerContent}
        </Drawer>
      ) : (
        /* Desktop Permanent Drawer */
        <Drawer
          variant="permanent"
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: theme.palette.background.paper,
              borderRight: `1px solid ${theme.palette.divider}`,
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      )}
    </Box>
  );
};

export default Sidebar;