import { useRuntimeConfig } from '#app'

interface LoginData {
  email: string
  password: string
}

interface RegisterData {
  nom: string
  prenom: string
  email: string
  password: string
  telephone?: string
  localisation?: string
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
  static buildPhotoUrl(photoPath: string | null): string {
    if (!photoPath) return '';
    if (photoPath.startsWith('http')) return photoPath;
    console.log(photoPath)
    return `${this.getBaseUrl()}/${photoPath}`;
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
      const requestData = {
        nom: data.nom,
        prenom: data.prenom,
        email: data.email,
        password: data.password,
        telephone: data.telephone,
        localisation: data.localisation
      };

      const response = await fetch(`${this.getBaseUrl()}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestData),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Erreur lors de l\'inscription');
      }

      return { success: true, data: result };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Une erreur est survenue lors de l\'inscription'
      };
    }
  }

  static async logout(): Promise<void> {
    localStorage.removeItem('token')
  }

  static isAuthenticated(): boolean {
    return !!localStorage.getItem('token')
  }

  static async createPlant(data: PlantCreateData): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('name', data.name);
      formData.append('type', data.type);
      formData.append('location', data.location);
      formData.append('needs', data.needs);

      // Si la photo existe, ajouter l'image au FormData
      if (data.photo) {
        formData.append('photo', data.photo);
      }

      const token = localStorage.getItem('token');
      const response = await fetch(`${this.getBaseUrl()}/plants/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Erreur lors de l\'ajout de la plante');
      }

      return { success: true, data: result };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Une erreur est survenue lors de l\'ajout de la plante'
      };
    }
  }

  
static async getPlants(): Promise<ApiResponse<any>> {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${this.getBaseUrl()}/plants/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || 'Erreur lors de la récupération des plantes');
    }

    return { success: true, data: result };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Une erreur est survenue lors de la récupération des plantes',
    };
  }
}
} 