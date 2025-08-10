// Token storage keys
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_EXPIRY_KEY = 'token_expiry';

export interface TokenData {
  accessToken: string;
  refreshToken?: string;
  expiresIn?: number;
}

export class AuthTokenManager {
  private static instance: AuthTokenManager;
  private refreshPromise: Promise<boolean> | null = null;

  private constructor() {}

  static getInstance(): AuthTokenManager {
    if (!AuthTokenManager.instance) {
      AuthTokenManager.instance = new AuthTokenManager();
    }
    return AuthTokenManager.instance;
  }

  // Token Storage Methods
  setTokens(data: TokenData): void {
    if (typeof window === 'undefined') return;

    localStorage.setItem(TOKEN_KEY, data.accessToken);
    
    if (data.refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken);
    }
    
    if (data.expiresIn) {
      const expiryTime = Date.now() + data.expiresIn * 1000;
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
    }
  }

  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  removeTokens(): void {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
  }

  // Token Validation Methods
  isTokenExpired(): boolean {
    if (typeof window === 'undefined') return true;
    
    const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY);
    if (!expiryTime) return true;
    
    return Date.now() > parseInt(expiryTime, 10);
  }

  getTimeUntilExpiry(): number {
    if (typeof window === 'undefined') return 0;
    
    const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY);
    if (!expiryTime) return 0;
    
    const timeLeft = parseInt(expiryTime, 10) - Date.now();
    return Math.max(0, timeLeft);
  }

  // Token Refresh Methods
  async refreshToken(): Promise<boolean> {
    // Prevent multiple simultaneous refresh attempts
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.performTokenRefresh();
    
    try {
      const result = await this.refreshPromise;
      return result;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async performTokenRefresh(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        this.removeTokens();
        return false;
      }

      const data = await response.json();
      
      this.setTokens({
        accessToken: data.access_token,
        refreshToken: data.refresh_token || refreshToken,
        expiresIn: data.expires_in,
      });

      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.removeTokens();
      return false;
    }
  }

  // Auto-refresh setup
  setupAutoRefresh(): void {
    if (typeof window === 'undefined') return;

    // Check token expiry every minute
    setInterval(() => {
      const timeUntilExpiry = this.getTimeUntilExpiry();
      
      // Refresh token if it expires in less than 5 minutes
      if (timeUntilExpiry > 0 && timeUntilExpiry < 5 * 60 * 1000) {
        this.refreshToken();
      }
    }, 60 * 1000); // Check every minute
  }
}

// Export singleton instance
export default AuthTokenManager.getInstance();
