import { getApiClient } from '@/lib/api/client';
import { AuthTokenManager } from '@/lib/auth/tokenManager';
import { API_ENDPOINTS, SUCCESS_MESSAGES, ERROR_MESSAGES } from '@/lib/constants';

export interface SignUpData {
  email: string;
  password: string;
  full_name: string;
  phone_number: string;
}

export interface SignInData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  phone_number: string;
  is_active: boolean;
  is_verified: boolean;
  role: string;
  created_at: string;
  total_bookings: number;
}

class AuthService {
  private static instance: AuthService;
  private apiClient = getApiClient();
  private tokenManager = AuthTokenManager.getInstance();
  
  private constructor() {
    // Setup auto token refresh
    this.tokenManager.setupAutoRefresh();
  }
  
  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async signUp(data: SignUpData): Promise<UserResponse> {
    try {
      console.log('Attempting to sign up with data:', { ...data, password: '[HIDDEN]' });
      
      const response = await this.apiClient.post<UserResponse>(
        API_ENDPOINTS.AUTH.REGISTER,
        data
      );

      console.log('Sign up successful');
      return response;
    } catch (error: any) {
      console.error('Sign up error:', error);
      
      // Provide user-friendly error messages
      if (error.status === 409) {
        throw new Error('An account with this email already exists');
      } else if (error.status === 400) {
        throw new Error(error.message || 'Invalid registration data');
      } else if (error.name === 'NetworkError') {
        throw new Error(ERROR_MESSAGES.NETWORK);
      }
      
      throw new Error(error.message || ERROR_MESSAGES.GENERIC);
    }
  }

  async signIn(data: SignInData): Promise<AuthResponse> {
    try {
      console.log('Attempting to sign in with email:', data.email);
      
      const response = await this.apiClient.post<AuthResponse>(
        API_ENDPOINTS.AUTH.LOGIN,
        data
      );

      console.log('Sign in successful');
      
      // Store tokens
      this.tokenManager.setTokens({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        expiresIn: response.expires_in,
      });
      
      return response;
    } catch (error: any) {
      console.error('Sign in error:', error);
      
      // Provide user-friendly error messages
      if (error.status === 401) {
        throw new Error('Invalid email or password');
      } else if (error.status === 429) {
        throw new Error('Too many login attempts. Please try again later.');
      } else if (error.name === 'NetworkError') {
        throw new Error(ERROR_MESSAGES.NETWORK);
      }
      
      throw new Error(error.message || ERROR_MESSAGES.GENERIC);
    }
  }

  async signOut(): Promise<void> {
    try {
      // Try to call logout endpoint if available
      await this.apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      // Ignore errors from logout endpoint
      console.error('Logout endpoint error:', error);
    } finally {
      // Always remove tokens locally
      this.tokenManager.removeTokens();
    }
  }

  getToken(): string | null {
    return this.tokenManager.getToken();
  }

  isAuthenticated(): boolean {
    const token = this.tokenManager.getToken();
    if (!token) return false;
    
    // Check if token is expired
    if (this.tokenManager.isTokenExpired()) {
      // Try to refresh
      this.tokenManager.refreshToken().catch(() => {
        // If refresh fails, user needs to login again
        this.tokenManager.removeTokens();
      });
      return false;
    }
    
    return true;
  }

  async getCurrentUser(): Promise<UserResponse> {
    try {
      const response = await this.apiClient.get<UserResponse>(
        API_ENDPOINTS.USERS.ME
      );
      
      return response;
    } catch (error: any) {
      console.error('Get current user error:', error);
      
      if (error.status === 401) {
        throw new Error(ERROR_MESSAGES.UNAUTHORIZED);
      }
      
      throw new Error(error.message || ERROR_MESSAGES.GENERIC);
    }
  }
}

export default AuthService.getInstance();
