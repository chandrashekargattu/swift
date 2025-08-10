import { AuthTokenManager } from '@/lib/auth/tokenManager';

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000, // 30 seconds
  RETRY_COUNT: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

// Error Types
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class NetworkError extends Error {
  constructor(message: string = 'Network connection failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class TimeoutError extends Error {
  constructor(message: string = 'Request timed out') {
    super(message);
    this.name = 'TimeoutError';
  }
}

// Request interceptor type
type RequestInterceptor = (config: RequestInit) => RequestInit | Promise<RequestInit>;
type ResponseInterceptor = (response: Response) => Response | Promise<Response>;

// API Client Class
export class ApiClient {
  private baseURL: string;
  private timeout: number;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private tokenManager: AuthTokenManager;

  constructor(baseURL: string = API_CONFIG.BASE_URL, timeout: number = API_CONFIG.TIMEOUT) {
    this.baseURL = baseURL;
    this.timeout = timeout;
    this.tokenManager = AuthTokenManager.getInstance();
    this.setupDefaultInterceptors();
  }

  private setupDefaultInterceptors() {
    // Request interceptor for auth token
    this.addRequestInterceptor((config) => {
      const token = this.tokenManager.getToken();
      if (token) {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${token}`,
        };
      }
      return config;
    });

    // Response interceptor for token refresh
    this.addResponseInterceptor(async (response) => {
      if (response.status === 401) {
        // Token might be expired, try to refresh
        const refreshed = await this.tokenManager.refreshToken();
        if (!refreshed) {
          // Redirect to login if refresh fails
          window.location.href = '/signin';
        }
      }
      return response;
    });
  }

  addRequestInterceptor(interceptor: RequestInterceptor) {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: ResponseInterceptor) {
    this.responseInterceptors.push(interceptor);
  }

  private async applyRequestInterceptors(config: RequestInit): Promise<RequestInit> {
    let modifiedConfig = config;
    for (const interceptor of this.requestInterceptors) {
      modifiedConfig = await interceptor(modifiedConfig);
    }
    return modifiedConfig;
  }

  private async applyResponseInterceptors(response: Response): Promise<Response> {
    let modifiedResponse = response;
    for (const interceptor of this.responseInterceptors) {
      modifiedResponse = await interceptor(modifiedResponse);
    }
    return modifiedResponse;
  }

  private async fetchWithTimeout(
    url: string,
    config: RequestInit,
    timeout: number
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new TimeoutError();
      }
      throw error;
    }
  }

  private async retryRequest(
    url: string,
    config: RequestInit,
    retries: number = API_CONFIG.RETRY_COUNT
  ): Promise<Response> {
    let lastError: Error | null = null;

    for (let i = 0; i <= retries; i++) {
      try {
        return await this.fetchWithTimeout(url, config, this.timeout);
      } catch (error: any) {
        lastError = error;
        
        // Don't retry on client errors (4xx)
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
          throw error;
        }

        // Don't retry if it's the last attempt
        if (i === retries) {
          throw error;
        }

        // Wait before retrying with exponential backoff
        const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, i);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError || new Error('Request failed after retries');
  }

  async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    console.log('API Request:', {
      baseURL: this.baseURL,
      endpoint,
      fullUrl: url,
      method: options.method || 'GET'
    });
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...options.headers,
      },
    };

    try {
      // Apply request interceptors
      const modifiedConfig = await this.applyRequestInterceptors(config);

      // Make request with retry logic
      let response = await this.retryRequest(url, modifiedConfig);

      // Apply response interceptors
      response = await this.applyResponseInterceptors(response);

      // Handle response
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Handle backend error format { error: { message, code, details } }
        const errorInfo = errorData.error || errorData;
        const message = errorInfo.message || errorInfo.detail || 'Request failed';
        const code = errorInfo.code || response.status;
        
        throw new ApiError(
          message,
          response.status,
          code,
          errorInfo
        );
      }

      // Parse response
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return response as any;
    } catch (error: any) {
      // Handle network errors
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new NetworkError();
      }
      
      // Re-throw known errors
      if (error instanceof ApiError || error instanceof NetworkError || error instanceof TimeoutError) {
        throw error;
      }
      
      // Wrap unknown errors
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }

  // Convenience methods
  async get<T = any>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T = any>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

// Singleton instance
let apiClientInstance: ApiClient | null = null;

export function getApiClient(): ApiClient {
  if (!apiClientInstance) {
    apiClientInstance = new ApiClient();
  }
  return apiClientInstance;
}

// Export default instance
export const apiClient = getApiClient();
export default apiClient;
