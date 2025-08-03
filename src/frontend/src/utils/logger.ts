/**
 * Centralized logging system for Karui-Search frontend
 * Provides structured logging with different levels and contexts
 */

import log from 'loglevel';

// Configure log levels based on environment
const isDevelopment = import.meta.env.DEV;
const isTest = import.meta.env.MODE === 'test';

// Set appropriate log level
if (isTest) {
  log.setLevel('SILENT');
} else if (isDevelopment) {
  log.setLevel('DEBUG');
} else {
  log.setLevel('WARN');
}

export interface LogContext {
  component?: string;
  action?: string;
  userId?: string;
  sessionId?: string;
  propertyId?: string;
  metadata?: Record<string, any>;
}

class Logger {
  private context: LogContext = {};

  setContext(context: LogContext) {
    this.context = { ...this.context, ...context };
  }

  clearContext() {
    this.context = {};
  }

  private formatMessage(level: string, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const ctx = { ...this.context, ...context };
    
    const logEntry = {
      timestamp,
      level,
      message,
      context: ctx,
      url: window?.location?.href,
      userAgent: navigator?.userAgent?.substring(0, 100)
    };

    return JSON.stringify(logEntry, null, isDevelopment ? 2 : 0);
  }

  debug(message: string, context?: LogContext) {
    if (!isTest) {
      log.debug(this.formatMessage('DEBUG', message, context));
    }
  }

  info(message: string, context?: LogContext) {
    if (!isTest) {
      log.info(this.formatMessage('INFO', message, context));
    }
  }

  warn(message: string, context?: LogContext) {
    log.warn(this.formatMessage('WARN', message, context));
  }

  error(message: string, error?: Error, context?: LogContext) {
    const errorContext = {
      ...context,
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack
      } : undefined
    };
    
    log.error(this.formatMessage('ERROR', message, errorContext));
    
    // In production, could send to error tracking service
    if (!isDevelopment && !isTest) {
      this.sendToErrorTracking(message, error, errorContext);
    }
  }

  // Property-specific logging methods
  propertyViewed(propertyId: string, source: string) {
    this.info('Property viewed', {
      action: 'property_viewed',
      propertyId,
      source,
      metadata: { source }
    });
  }

  propertyFiltered(filters: Record<string, any>) {
    this.debug('Properties filtered', {
      action: 'properties_filtered',
      metadata: { filters }
    });
  }

  searchPerformed(query: string, resultsCount: number) {
    this.info('Search performed', {
      action: 'search_performed',
      metadata: { query, resultsCount }
    });
  }

  pageNavigation(from: string, to: string, method: string = 'click') {
    this.debug('Page navigation', {
      action: 'page_navigation',
      metadata: { from, to, method }
    });
  }

  apiRequest(endpoint: string, method: string, duration?: number) {
    this.debug('API request', {
      action: 'api_request',
      metadata: { endpoint, method, duration }
    });
  }

  apiResponse(endpoint: string, status: number, duration: number) {
    const level = status >= 400 ? 'ERROR' : 'DEBUG';
    const message = `API response: ${endpoint} (${status}) in ${duration}ms`;
    
    if (level === 'ERROR') {
      this.error(message, undefined, {
        action: 'api_response',
        metadata: { endpoint, status, duration }
      });
    } else {
      this.debug(message, {
        action: 'api_response',
        metadata: { endpoint, status, duration }
      });
    }
  }

  performanceMetric(metric: string, value: number, unit: string = 'ms') {
    this.debug(`Performance: ${metric}`, {
      action: 'performance_metric',
      metadata: { metric, value, unit }
    });
  }

  userInteraction(component: string, action: string, metadata?: Record<string, any>) {
    this.debug(`User interaction: ${component}.${action}`, {
      action: 'user_interaction',
      component,
      metadata
    });
  }

  languageChanged(from: string, to: string) {
    this.info('Language changed', {
      action: 'language_changed',
      metadata: { from, to }
    });
  }

  private sendToErrorTracking(message: string, error?: Error, context?: LogContext) {
    // Placeholder for production error tracking integration
    // Could integrate with services like Sentry, LogRocket, etc.
    console.warn('Error tracking not implemented:', { message, error, context });
  }
}

// Create singleton logger instance
export const logger = new Logger();

// Development helpers
if (isDevelopment) {
  // Make logger available in browser console for debugging
  (window as any).logger = logger;
  
  // Log application startup
  logger.info('Karui-Search frontend started', {
    action: 'app_startup',
    metadata: {
      environment: import.meta.env.MODE,
      version: '1.0.0',
      buildTime: new Date().toISOString()
    }
  });
}

// Export individual methods for convenience
export const {
  debug,
  info,
  warn,
  error,
  propertyViewed,
  propertyFiltered,
  searchPerformed,
  pageNavigation,
  apiRequest,
  apiResponse,
  performanceMetric,
  userInteraction,
  languageChanged
} = logger;

export default logger;