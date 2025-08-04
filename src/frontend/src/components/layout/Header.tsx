/**
 * Header Component
 * Top navigation bar with logo, search, and language toggle
 * Responsive design with mobile menu toggle
 */

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Box,
  InputBase,
  alpha,
  useTheme,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Translate as TranslateIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { logger } from '@utils/logger';

interface HeaderProps {
  drawerWidth: number;
  onDrawerToggle: () => void;
  isMobile: boolean;
}

const Header: React.FC<HeaderProps> = ({
  drawerWidth,
  onDrawerToggle,
  isMobile,
}) => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();

  const handleLanguageToggle = () => {
    const newLanguage = i18n.language === 'ja' ? 'en' : 'ja';
    i18n.changeLanguage(newLanguage);
    logger.userInteraction('Header', 'language_toggle', {
      from: i18n.language,
      to: newLanguage
    });
  };

  const handleSearch = (searchTerm: string) => {
    logger.userInteraction('Header', 'search', {
      searchTerm: searchTerm.length > 0 ? '[search_performed]' : '[search_cleared]'
    });
    // TODO: Implement search functionality
  };

  const handleNotificationsClick = () => {
    logger.userInteraction('Header', 'notifications_click');
    // TODO: Implement notifications
  };

  const handleSettingsClick = () => {
    logger.userInteraction('Header', 'settings_click');
    // TODO: Implement settings
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        width: isMobile ? '100%' : `calc(100% - ${drawerWidth}px)`,
        marginLeft: isMobile ? 0 : `${drawerWidth}px`,
        transition: theme.transitions.create(['width', 'margin'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.primary.contrastText,
      }}
      data-testid="app-header"
    >
      <Toolbar sx={{ minHeight: '64px !important' }}>
        {/* Mobile Menu Toggle */}
        {isMobile && (
          <IconButton
            color="inherit"
            aria-label={t('navigation.openMenu')}
            edge="start"
            onClick={onDrawerToggle}
            sx={{ mr: 2 }}
            data-testid="mobile-menu-toggle"
          >
            <MenuIcon />
          </IconButton>
        )}

        {/* Logo and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 0 }}>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{
              fontWeight: 600,
              fontSize: { xs: '1.1rem', sm: '1.25rem' },
              color: 'inherit',
            }}
          >
            {t('app.title')}
          </Typography>
          <Typography
            variant="caption"
            sx={{
              ml: 1,
              opacity: 0.8,
              display: { xs: 'none', sm: 'inline' },
            }}
          >
            {t('app.subtitle')}
          </Typography>
        </Box>

        {/* Search Bar */}
        <Box
          sx={{
            position: 'relative',
            borderRadius: theme.shape.borderRadius,
            backgroundColor: alpha(theme.palette.common.white, 0.15),
            '&:hover': {
              backgroundColor: alpha(theme.palette.common.white, 0.25),
            },
            marginLeft: theme.spacing(2),
            marginRight: theme.spacing(2),
            width: 'auto',
            flexGrow: 1,
            maxWidth: { xs: 'none', sm: 400 },
            display: { xs: 'none', sm: 'block' },
          }}
        >
          <Box
            sx={{
              padding: theme.spacing(0, 2),
              height: '100%',
              position: 'absolute',
              pointerEvents: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <SearchIcon />
          </Box>
          <InputBase
            placeholder={t('search.placeholder')}
            inputProps={{ 'aria-label': t('search.placeholder') }}
            sx={{
              color: 'inherit',
              width: '100%',
              '& .MuiInputBase-input': {
                padding: theme.spacing(1, 1, 1, 0),
                paddingLeft: `calc(1em + ${theme.spacing(4)})`,
                transition: theme.transitions.create('width'),
                width: '100%',
              },
            }}
            onChange={(e) => handleSearch(e.target.value)}
            data-testid="search-input"
          />
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Mobile Search Icon */}
          <IconButton
            color="inherit"
            aria-label={t('search.placeholder')}
            sx={{ display: { xs: 'block', sm: 'none' } }}
            data-testid="mobile-search-button"
          >
            <SearchIcon />
          </IconButton>

          {/* Language Toggle */}
          <Tooltip title={t('common.changeLanguage')}>
            <Button
              color="inherit"
              onClick={handleLanguageToggle}
              startIcon={<TranslateIcon />}
              sx={{
                minWidth: 'auto',
                px: { xs: 1, sm: 2 },
                '& .MuiButton-startIcon': {
                  marginRight: { xs: 0, sm: 1 },
                },
              }}
              data-testid="language-toggle"
            >
              <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
                {i18n.language.toUpperCase()}
              </Box>
            </Button>
          </Tooltip>

          {/* Notifications */}
          <Tooltip title={t('common.notifications')}>
            <IconButton
              color="inherit"
              aria-label={t('common.notifications')}
              onClick={handleNotificationsClick}
              data-testid="notifications-button"
            >
              <NotificationsIcon />
            </IconButton>
          </Tooltip>

          {/* Settings */}
          <Tooltip title={t('common.settings')}>
            <IconButton
              color="inherit"
              aria-label={t('common.settings')}
              onClick={handleSettingsClick}
              sx={{ display: { xs: 'none', sm: 'block' } }}
              data-testid="settings-button"
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;