import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    nombre_completo: string;
    rol: string;
  };
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await api.post('/auth/login', formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const data = response.data;
    
    // Guardar token de forma segura
    await SecureStore.setItemAsync('access_token', data.access_token);
    await AsyncStorage.setItem('user_data', JSON.stringify(data.user));
    
    return data;
  }

  async logout(): Promise<void> {
    await SecureStore.deleteItemAsync('access_token');
    await AsyncStorage.removeItem('user_data');
    await AsyncStorage.removeItem('paciente_id');
  }

  async getStoredToken(): Promise<string | null> {
    return await SecureStore.getItemAsync('access_token');
  }

  async getStoredUser(): Promise<any> {
    const userData = await AsyncStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  async isAuthenticated(): Promise<boolean> {
    const token = await this.getStoredToken();
    return !!token;
  }

  async setPacienteId(pacienteId: string): Promise<void> {
    await AsyncStorage.setItem('paciente_id', pacienteId);
  }

  async getPacienteId(): Promise<string | null> {
    return await AsyncStorage.getItem('paciente_id');
  }
}

export default new AuthService();
