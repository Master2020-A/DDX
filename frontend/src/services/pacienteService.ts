import api from '@/lib/api';

export const pacienteService = {
  listar: async () => {
    const response = await api.get('/pacientes/basico');
    return response.data;
  },

  obtener: async (id: string) => {
    const response = await api.get(`/pacientes/${id}`);
    return response.data;
  },

  crear: async (data: any) => {
    const response = await api.post('/pacientes', data);
    return response.data;
  },

  actualizar: async (id: string, data: any) => {
    const response = await api.put(`/pacientes/${id}`, data);
    return response.data;
  },

  eliminar: async (id: string) => {
    const response = await api.delete(`/pacientes/${id}`);
    return response.data;
  }
};
