import { useRuntimeConfig } from '#app'

interface LoginData {
  email: string
  password: string
}

interface RegisterData {
  username: string
  email: string
  password: string
}

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export class ApiService {
  private static getBaseUrl(): string {
    return useRuntimeConfig().public.apiUrl
  }

  static async login(data: LoginData): Promise<ApiResponse<any>> {
    try {
      const formData = new URLSearchParams()
      formData.append('username', data.email)
      formData.append('password', data.password)

      const response = await fetch(`${this.getBaseUrl()}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })

      const result = await response.json()
      console.log(result)

      if (!response.ok) {
        throw new Error(result.detail || 'Erreur de connexion')
      }

      // Stocker le token dans le localStorage
      if (result.access_token) {
        localStorage.setItem('token', result.access_token)
      }

      return { success: true, data: result }
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Une erreur est survenue lors de la connexion'
      }
    }
  }

  static async register(data: RegisterData): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail || 'Erreur lors de l\'inscription')
      }

      return { success: true, data: result }
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Une erreur est survenue lors de l\'inscription'
      }
    }
  }

  static async logout(): Promise<void> {
    localStorage.removeItem('token')
  }

  static isAuthenticated(): boolean {
    return !!localStorage.getItem('token')
  }
} 