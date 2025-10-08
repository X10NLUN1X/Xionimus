/**
 * Enhanced API Client with Retry Logic and Better Error Handling
 * Automatically retries failed requests and provides better error messages
 */

import API_CONFIG from './api';

export interface RetryConfig {
  maxRetries?: number;
  retryDelay?: number;
  retryOn?: (error: any) => boolean;
}

const DEFAULT_RETRY_CONFIG: Required<RetryConfig> = {
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  retryOn: (error: any) => {
    // Retry on network errors or 5xx server errors
    if (error.message?.includes('Network Error')) return true;
    if (error.message?.includes('Failed to fetch')) return true;
    if (error.status >= 500 && error.status < 600) return true;
    return false;
  }
};

class EnhancedAPIClient {
  private requestInProgress = new Map<string, Promise<any>>();

  /**
   * Make API call with automatic retry
   */
  async callWithRetry<T = any>(
    endpoint: string,
    options: RequestInit = {},
    retryConfig: RetryConfig = {}
  ): Promise<T> {
    const config = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
    let lastError: any;

    for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
      try {
        // Deduplicate identical concurrent requests
        const requestKey = `${endpoint}:${JSON.stringify(options)}`;
        
        if (this.requestInProgress.has(requestKey)) {
          console.log(`🔄 Deduplicating request to ${endpoint}`);
          return await this.requestInProgress.get(requestKey);
        }

        const requestPromise = this.makeRequest<T>(endpoint, options);
        this.requestInProgress.set(requestKey, requestPromise);

        try {
          const result = await requestPromise;
          this.requestInProgress.delete(requestKey);
          return result;
        } catch (error) {
          this.requestInProgress.delete(requestKey);
          throw error;
        }
      } catch (error: any) {
        lastError = error;

        // Check if should retry
        if (attempt < config.maxRetries && config.retryOn(error)) {
          console.warn(
            `⚠️ Request failed (attempt ${attempt + 1}/${config.maxRetries + 1}):`,
            error.message
          );
          console.log(`🔄 Retrying in ${config.retryDelay}ms...`);
          
          // Wait before retry
          await this.delay(config.retryDelay);
          
          // Exponential backoff
          config.retryDelay *= 2;
          continue;
        }

        // Don't retry
        break;
      }
    }

    // All retries failed
    throw this.enhanceError(lastError, endpoint);
  }

  /**
   * Make single API request
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = API_CONFIG.url(endpoint);
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      API_CONFIG.TIMEOUT
    );

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          ...API_CONFIG.getHeaders(),
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          message: `HTTP ${response.status}: ${response.statusText}`
        }));
        
        const apiError: any = new Error(error.message || `HTTP ${response.status}`);
        apiError.status = response.status;
        apiError.response = error;
        throw apiError;
      }

      return response.json();
    } catch (error: any) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        const timeoutError: any = new Error(`Request timeout after ${API_CONFIG.TIMEOUT}ms`);
        timeoutError.isTimeout = true;
        throw timeoutError;
      }

      throw error;
    }
  }

  /**
   * Enhance error with more context
   */
  private enhanceError(error: any, endpoint: string): Error {
    const enhanced: any = new Error(
      this.getUserFriendlyMessage(error)
    );
    
    enhanced.originalError = error;
    enhanced.endpoint = endpoint;
    enhanced.timestamp = new Date().toISOString();

    return enhanced;
  }

  /**
   * Get user-friendly error message
   */
  private getUserFriendlyMessage(error: any): string {
    if (error.isTimeout) {
      return 'Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es erneut.';
    }

    if (error.message?.includes('Failed to fetch') || 
        error.message?.includes('Network Error')) {
      return 'Keine Verbindung zum Server. Bitte prüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.';
    }

    if (error.status === 401) {
      return 'Bitte melden Sie sich erneut an.';
    }

    if (error.status === 403) {
      return 'Sie haben keine Berechtigung für diese Aktion.';
    }

    if (error.status === 404) {
      return 'Die angeforderte Ressource wurde nicht gefunden.';
    }

    if (error.status >= 500) {
      return 'Ein Serverfehler ist aufgetreten. Bitte versuchen Sie es später erneut.';
    }

    return error.message || 'Ein unbekannter Fehler ist aufgetreten.';
  }

  /**
   * Helper: Delay
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Check backend health
   */
  async checkHealth(): Promise<boolean> {
    try {
      await this.callWithRetry('/api/health', {}, {
        maxRetries: 1,
        retryDelay: 500
      });
      return true;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const enhancedAPI = new EnhancedAPIClient();

// Export for convenience
export default enhancedAPI;
