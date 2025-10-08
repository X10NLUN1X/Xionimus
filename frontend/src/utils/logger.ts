/**
 * Logger Utility
 * Centralized logging with production/development awareness
 * Replaces console.log with proper logging that can be disabled in production
 */

const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';
const IS_DEBUG = process.env.REACT_APP_DEBUG === 'true' || process.env.VITE_DEBUG === 'true';

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  data?: any;
  timestamp: string;
}

class Logger {
  private logHistory: LogEntry[] = [];
  private maxHistorySize = 100;

  /**
   * Log debug messages (only in development or when DEBUG=true)
   */
  debug(message: string, ...data: any[]) {
    if (IS_DEVELOPMENT || IS_DEBUG) {
      console.debug(`🐛 ${message}`, ...data);
      this.addToHistory('debug', message, data);
    }
  }

  /**
   * Log informational messages
   */
  info(message: string, ...data: any[]) {
    if (IS_DEVELOPMENT || IS_DEBUG) {
      console.info(`ℹ️ ${message}`, ...data);
      this.addToHistory('info', message, data);
    }
  }

  /**
   * Log warnings (always logged)
   */
  warn(message: string, ...data: any[]) {
    console.warn(`⚠️ ${message}`, ...data);
    this.addToHistory('warn', message, data);
  }

  /**
   * Log errors (always logged)
   */
  error(message: string, ...data: any[]) {
    console.error(`❌ ${message}`, ...data);
    this.addToHistory('error', message, data);
    
    // TODO: Send to error tracking service in production
    // if (!IS_DEVELOPMENT) {
    //   sendToErrorTracking(message, data);
    // }
  }

  /**
   * Log performance metrics
   */
  performance(name: string, duration: number) {
    if (IS_DEVELOPMENT || IS_DEBUG) {
      console.log(`📊 ${name}: ${duration.toFixed(2)}ms`);
    }
  }

  /**
   * Add entry to log history
   */
  private addToHistory(level: LogLevel, message: string, data?: any) {
    const entry: LogEntry = {
      level,
      message,
      data,
      timestamp: new Date().toISOString()
    };

    this.logHistory.push(entry);

    // Maintain max history size
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.shift();
    }
  }

  /**
   * Get log history
   */
  getHistory(): LogEntry[] {
    return [...this.logHistory];
  }

  /**
   * Clear log history
   */
  clearHistory() {
    this.logHistory = [];
  }

  /**
   * Export logs for debugging
   */
  exportLogs(): string {
    return JSON.stringify(this.logHistory, null, 2);
  }
}

// Create singleton instance
const logger = new Logger();

// Export logger instance
export default logger;

// Export convenience functions
export const log = {
  debug: (message: string, ...data: any[]) => logger.debug(message, ...data),
  info: (message: string, ...data: any[]) => logger.info(message, ...data),
  warn: (message: string, ...data: any[]) => logger.warn(message, ...data),
  error: (message: string, ...data: any[]) => logger.error(message, ...data),
  performance: (name: string, duration: number) => logger.performance(name, duration),
  getHistory: () => logger.getHistory(),
  clearHistory: () => logger.clearHistory(),
  exportLogs: () => logger.exportLogs()
};