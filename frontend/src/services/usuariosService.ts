import api from './api';

interface Usuario {
  id: string;
  nombre_completo: string;
  email: string;
  username: string;
  activo: boolean;
  created_at: string;
  rol?: string;
}

const usuariosService = {
  async getUsuarios(): Promise<Usuario[]> {
    const response = await api.get('/security/users');
    return response.data;
  },

  async getUsuario(id: string): Promise<Usuario> {
    const response = await api.get(`/security/users/${id}`);
    return response.data;
  },

  async createUsuario(data: Partial<Usuario>): Promise<Usuario> {
    const response = await api.post('/security/users', data);
    return response.data;
  },

  async updateUsuario(id: string, data: Partial<Usuario>): Promise<Usuario> {
    const response = await api.put(`/security/users/${id}`, data);
    return response.data;
  },

  async deleteUsuario(id: string): Promise<void> {
    await api.delete(`/security/users/${id}`);
  }
};

export default usuariosService;
