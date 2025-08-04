/**
 * Main App Component
 * Root application component with routing, theming, and global providers
 * Integrates all core functionality for the Karui-Search application
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { I18nextProvider } from 'react-i18next';

// Components and Pages
import AppShell from '@components/layout/AppShell';
import Home from '@pages/Home';
import WeeklyReport from '@pages/WeeklyReport';
import AllListings from '@pages/AllListings';
import PropertyDetail from '@pages/PropertyDetail';
import Favorites from '@pages/Favorites';

// Services and Config
import { lightTheme } from '@utils/theme';
import i18n from '@i18n/index';
import { logger } from '@utils/logger';

// React Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logger.error('App Error Boundary caught error', {
      component: 'ErrorBoundary',
      action: 'error_caught',
      error: error.message,
      metadata: {
        stack: error.stack,
        componentStack: errorInfo.componentStack,
      }
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '2rem', 
          textAlign: 'center',
          fontFamily: 'Roboto, sans-serif'
        }}>
          <h1>アプリケーションエラーが発生しました</h1>
          <p>申し訳ございませんが、予期しないエラーが発生しました。</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#2E7D32',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            ページを再読み込み
          </button>
          {import.meta.env.DEV && (
            <details style={{ marginTop: '1rem', textAlign: 'left' }}>
              <summary>Error Details (Development)</summary>
              <pre style={{ 
                background: '#f5f5f5', 
                padding: '1rem', 
                borderRadius: '4px',
                overflow: 'auto',
                fontSize: '0.8rem'
              }}>
                {this.state.error?.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

// Loading Component for Route Lazy Loading
const RouteLoader: React.FC = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '200px',
    fontFamily: 'Roboto, sans-serif',
    color: '#666'
  }}>
    読み込み中...
  </div>
);

// 404 Not Found Component
const NotFound: React.FC = () => (
  <div style={{
    padding: '4rem 2rem',
    textAlign: 'center',
    fontFamily: 'Roboto, sans-serif'
  }}>
    <h1>404 - ページが見つかりません</h1>
    <p>お探しのページは存在しません。</p>
    <a 
      href="/" 
      style={{
        color: '#2E7D32',
        textDecoration: 'none',
        fontWeight: 'bold'
      }}
    >
      ホームに戻る
    </a>
  </div>
);

const App: React.FC = () => {
  // Log app initialization
  React.useEffect(() => {
    logger.info('App initialized', {
      component: 'App',
      action: 'app_start',
      metadata: {
        version: '1.0.0',
        environment: import.meta.env.MODE,
        language: i18n.language,
        timestamp: new Date().toISOString(),
      }
    });

    // Log browser and device info
    logger.debug('Browser info', {
      component: 'App',
      action: 'browser_info',
      metadata: {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        screenResolution: `${screen.width}x${screen.height}`,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
      }
    });

    // Performance logging
    if ('performance' in window) {
      window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        logger.info('App load performance', {
          component: 'App',
          action: 'performance_metrics',
          metadata: {
            domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
            loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
            totalLoadTime: perfData.loadEventEnd - perfData.fetchStart,
          }
        });
      });
    }

    // Cleanup function
    return () => {
      logger.debug('App cleanup', {
        component: 'App',
        action: 'app_cleanup'
      });
    };
  }, []);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={lightTheme}>
          <I18nextProvider i18n={i18n}>
            <CssBaseline />
            <Router>
              <AppShell>
                <Routes>
                  {/* Main Routes */}
                  <Route path="/" element={<Home />} />
                  <Route path="/weekly" element={<WeeklyReport />} />
                  <Route path="/listings" element={<AllListings />} />
                  <Route path="/property/:id" element={<PropertyDetail />} />

                  {/* Redirect Routes */}
                  <Route path="/home" element={<Navigate to="/" replace />} />
                  <Route path="/reports" element={<Navigate to="/weekly" replace />} />
                  <Route path="/properties" element={<Navigate to="/listings" replace />} />

                  {/* Favorites Route */}
                  <Route path="/favorites" element={<Favorites />} />

                  {/* Placeholder Routes for Future Implementation */}
                  <Route 
                    path="/analysis" 
                    element={
                      <div style={{ padding: '2rem', textAlign: 'center' }}>
                        <h2>価格分析機能</h2>
                        <p>この機能は近日公開予定です。</p>
                      </div>
                    } 
                  />
                  <Route 
                    path="/history" 
                    element={
                      <div style={{ padding: '2rem', textAlign: 'center' }}>
                        <h2>検索履歴</h2>
                        <p>この機能は近日公開予定です。</p>
                      </div>
                    } 
                  />
                  <Route 
                    path="/settings" 
                    element={
                      <div style={{ padding: '2rem', textAlign: 'center' }}>
                        <h2>設定</h2>
                        <p>この機能は近日公開予定です。</p>
                      </div>
                    } 
                  />

                  {/* 404 Route */}
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </AppShell>
            </Router>

            {/* Development Tools */}
            {import.meta.env.DEV && (
              <ReactQueryDevtools 
                initialIsOpen={false} 
                position="bottom-right"
              />
            )}
          </I18nextProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;