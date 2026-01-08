import api from '@/lib/api';

export interface SearchResult {
  id: string;
  tipo: 'paciente' | 'interconsulta';
  titulo: string;
  subtitulo: string;
  url: string;
  icono: string;
}

export interface SearchResponse {
  pacientes: SearchResult[];
  interconsultas: SearchResult[];
  query: string;
}

export const searchService = {
  buscar: async (query: string): Promise<SearchResponse> => {
    const response = await api.get('/search/', { params: { q: query, limit: 10 } });
    return response.data;
  },
};