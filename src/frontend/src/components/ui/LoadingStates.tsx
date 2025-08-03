/**
 * LoadingStates Component
 * Various loading states and placeholders with Japanese aesthetics
 * Includes skeletons, spinners, and empty states
 */

import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  LinearProgress,
  Skeleton,
  Card,
  CardContent,
  Button,
  useTheme,
} from '@mui/material';
import {
  SearchIcon,
  HomeIcon,
  RefreshIcon,
  ErrorOutlineIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

// Loading Spinner Component
export const LoadingSpinner: React.FC<{
  size?: number;
  message?: string;
  fullScreen?: boolean;
}> = ({ size = 40, message, fullScreen = false }) => {
  const { t } = useTranslation();
  const theme = useTheme();

  const content = (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      gap={2}
      sx={{ p: 4 }}
    >
      <CircularProgress size={size} color="primary" />
      {message && (
        <Typography variant="body2" color="text.secondary" textAlign="center">
          {message}
        </Typography>
      )}
    </Box>
  );

  if (fullScreen) {
    return (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(2px)',
          zIndex: theme.zIndex.modal,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        data-testid="loading-spinner-fullscreen"
      >
        {content}
      </Box>
    );
  }

  return content;
};

// Linear Progress Bar
export const ProgressBar: React.FC<{
  progress?: number;
  message?: string;
  variant?: 'determinate' | 'indeterminate';
}> = ({ progress, message, variant = 'indeterminate' }) => {
  const theme = useTheme();

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {message && (
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {message}
        </Typography>
      )}
      <LinearProgress
        variant={variant}
        value={progress}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: theme.palette.grey[200],
          '& .MuiLinearProgress-bar': {
            borderRadius: 4,
          },
        }}
      />
      {variant === 'determinate' && progress !== undefined && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            {Math.round(progress)}%
          </Typography>
        </Box>
      )}
    </Box>
  );
};

// Property List Skeleton
export const PropertyListSkeleton: React.FC<{
  count?: number;
  compact?: boolean;
}> = ({ count = 6, compact = false }) => {
  return (
    <Box data-testid="property-list-skeleton">
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index} sx={{ mb: 2, height: compact ? 150 : 200 }}>
          <Box sx={{ display: 'flex', height: '100%' }}>
            <Skeleton
              variant="rectangular"
              width={compact ? 150 : 200}
              height="100%"
            />
            <CardContent sx={{ flex: 1 }}>
              <Skeleton variant="text" width="80%" height={24} />
              <Skeleton variant="text" width="60%" height={32} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="90%" height={20} />
              <Skeleton variant="text" width="70%" height={20} />
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Skeleton variant="rectangular" width={80} height={32} />
                <Skeleton variant="circular" width={32} height={32} />
                <Skeleton variant="circular" width={32} height={32} />
              </Box>
            </CardContent>
          </Box>
        </Card>
      ))}
    </Box>
  );
};

// Data Table Skeleton
export const TableSkeleton: React.FC<{
  rows?: number;
  columns?: number;
}> = ({ rows = 5, columns = 4 }) => {
  return (
    <Box data-testid="table-skeleton">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <Box
          key={rowIndex}
          sx={{
            display: 'flex',
            gap: 2,
            py: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
          }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton
              key={colIndex}
              variant="text"
              width={colIndex === 0 ? '40%' : '20%'}
              height={20}
            />
          ))}
        </Box>
      ))}
    </Box>
  );
};

// Empty State Component
export const EmptyState: React.FC<{
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  type?: 'search' | 'error' | 'general';
}> = ({ icon, title, description, action, type = 'general' }) => {
  const theme = useTheme();

  const getDefaultIcon = () => {
    switch (type) {
      case 'search':
        return <SearchIcon sx={{ fontSize: 64, color: theme.palette.text.disabled }} />;
      case 'error':
        return <ErrorOutlineIcon sx={{ fontSize: 64, color: theme.palette.error.main }} />;
      default:
        return <HomeIcon sx={{ fontSize: 64, color: theme.palette.text.disabled }} />;
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 4,
        textAlign: 'center',
        minHeight: 300,
      }}
      data-testid={`empty-state-${type}`}
    >
      {icon || getDefaultIcon()}
      
      <Typography
        variant="h6"
        color="text.secondary"
        sx={{ mt: 2, mb: 1, fontWeight: 500 }}
      >
        {title}
      </Typography>
      
      {description && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 3, maxWidth: 400 }}
        >
          {description}
        </Typography>
      )}
      
      {action && (
        <Button
          variant="outlined"
          onClick={action.onClick}
          startIcon={<RefreshIcon />}
          sx={{ mt: 1 }}
        >
          {action.label}
        </Button>
      )}
    </Box>
  );
};

// Error State Component
export const ErrorState: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
  showRetry?: boolean;
}> = ({ title, message, onRetry, showRetry = true }) => {
  const { t } = useTranslation();
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 6,
        px: 4,
        textAlign: 'center',
        backgroundColor: theme.palette.error.light + '08',
        borderRadius: 2,
        border: `1px solid ${theme.palette.error.light}`,
      }}
      data-testid="error-state"
    >
      <ErrorOutlineIcon
        sx={{
          fontSize: 48,
          color: theme.palette.error.main,
          mb: 2,
        }}
      />
      
      <Typography
        variant="h6"
        color="error.main"
        sx={{ mb: 1, fontWeight: 600 }}
      >
        {title || t('error.general')}
      </Typography>
      
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mb: 3, maxWidth: 400 }}
      >
        {message}
      </Typography>
      
      {showRetry && onRetry && (
        <Button
          variant="contained"
          color="error"
          onClick={onRetry}
          startIcon={<RefreshIcon />}
        >
          {t('common.retry')}
        </Button>
      )}
    </Box>
  );
};

// Inline Loading Component
export const InlineLoading: React.FC<{
  message?: string;
  size?: 'small' | 'medium';
}> = ({ message, size = 'medium' }) => {
  const spinnerSize = size === 'small' ? 16 : 20;

  return (
    <Box
      display="flex"
      alignItems="center"
      gap={1}
      sx={{ py: 1 }}
      data-testid="inline-loading"
    >
      <CircularProgress size={spinnerSize} />
      {message && (
        <Typography variant={size === 'small' ? 'caption' : 'body2'} color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );
};

// Page Loading Overlay
export const PageLoadingOverlay: React.FC<{
  message?: string;
}> = ({ message }) => {
  const { t } = useTranslation();
  const theme = useTheme();

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: theme.zIndex.modal - 1,
        backdropFilter: 'blur(1px)',
      }}
      data-testid="page-loading-overlay"
    >
      <CircularProgress size={40} color="primary" />
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mt: 2, textAlign: 'center' }}
      >
        {message || t('common.loading')}
      </Typography>
    </Box>
  );
};

export default {
  LoadingSpinner,
  ProgressBar,
  PropertyListSkeleton,
  TableSkeleton,
  EmptyState,
  ErrorState,
  InlineLoading,
  PageLoadingOverlay,
};