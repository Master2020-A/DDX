import axios from 'axios';
import {
  FHIRObservation,
  ObservationCreate,
  ObservationFromVitalSign,
  ObservationFromBloodPressure,
  ObservationFromLabParameter,
  ObservationBundle,
  ObservationStatistics,
  ObservationFilters
} from '../types/fhirObservation';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8612';
const BASE_PATH = '/api/fhir/observations';

class FHIRObservationService {
  private getAuthHeader() {
    const token = localStorage.getItem('token');
    return {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  }

  // Crear observación
  async createObservation(data: ObservationCreate): Promise<FHIRObservation> {
    const response = await axios.post(
      `${API_URL}${BASE_PATH}/`,
      data,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Listar observaciones con filtros
  async listObservations(filters?: ObservationFilters): Promise<FHIRObservation[]> {
    const params = new URLSearchParams();
    
    if (filters?.patient) params.append('patient', filters.patient);
    if (filters?.category) params.append('category', filters.category);
    if (filters?.code) params.append('code', filters.code);
    if (filters?.date) params.append('date', filters.date);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());

    const response = await axios.get(
      `${API_URL}${BASE_PATH}/?${params.toString()}`,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Obtener observación por ID
  async getObservation(id: string): Promise<FHIRObservation> {
    const response = await axios.get(
      `${API_URL}${BASE_PATH}/${id}`,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Actualizar observación
  async updateObservation(id: string, data: Partial<ObservationCreate>): Promise<FHIRObservation> {
    const response = await axios.put(
      `${API_URL}${BASE_PATH}/${id}`,
      data,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Eliminar observación
  async deleteObservation(id: string): Promise<void> {
    await axios.delete(
      `${API_URL}${BASE_PATH}/${id}`,
      this.getAuthHeader()
    );
  }

  // Obtener en formato FHIR completo
  async getObservationFHIR(id: string): Promise<any> {
    const response = await axios.get(
      `${API_URL}${BASE_PATH}/${id}/fhir`,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Obtener Bundle de paciente
  async getPatientBundle(patientId: string): Promise<ObservationBundle> {
    const response = await axios.get(
      `${API_URL}${BASE_PATH}/patient/${patientId}/bundle`,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Crear desde signo vital
  async createFromVitalSign(data: ObservationFromVitalSign): Promise<FHIRObservation> {
    const response = await axios.post(
      `${API_URL}${BASE_PATH}/from-vital-sign`,
      data,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Crear desde presión arterial
  async createFromBloodPressure(data: ObservationFromBloodPressure): Promise<FHIRObservation> {
    const response = await axios.post(
      `${API_URL}${BASE_PATH}/from-blood-pressure`,
      data,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Crear desde parámetro de laboratorio
  async createFromLabParameter(data: ObservationFromLabParameter): Promise<FHIRObservation> {
    const response = await axios.post(
      `${API_URL}${BASE_PATH}/from-lab-parameter`,
      data,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Obtener estadísticas
  async getStatistics(): Promise<ObservationStatistics> {
    const response = await axios.get(
      `${API_URL}${BASE_PATH}/statistics/summary`,
      this.getAuthHeader()
    );
    return response.data;
  }

  // Obtener observaciones por paciente (helper)
  async getObservationsByPatient(
    patientId: string,
    category?: string,
    limit: number = 50
  ): Promise<FHIRObservation[]> {
    return this.listObservations({
      patient: patientId,
      category: category as any,
      limit,
      skip: 0
    });
  }

  // Obtener signos vitales de un paciente
  async getVitalSigns(patientId: string, limit: number = 50): Promise<FHIRObservation[]> {
    return this.getObservationsByPatient(patientId, 'vital-signs', limit);
  }

  // Obtener resultados de laboratorio de un paciente
  async getLabResults(patientId: string, limit: number = 50): Promise<FHIRObservation[]> {
    return this.getObservationsByPatient(patientId, 'laboratory', limit);
  }
}

export default new FHIRObservationService();
