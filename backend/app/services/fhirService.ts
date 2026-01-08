// frontend/src/services/fhirService.ts
import axios from 'axios';

// Si ya tienes un apiClient central (por ej. en ./api.ts)
// importa eso en lugar de axios directamente:
// import apiClient from './api';

export interface FhirCarePlan {
  resourceType: 'CarePlan';
  id: string;
  status?: string;
  intent?: string;
  title?: string;
  description?: string;
  subject?: { reference?: string };
  author?: { reference?: string }[];
  created?: string;
  activity?: any[];
  note?: { text?: string }[];
  // Permitimos campos adicionales
  [key: string]: any;
}

export interface FhirMedicationRequest {
  resourceType: 'MedicationRequest';
  id: string;
  status?: string;
  intent?: string;
  medicationCodeableConcept?: { text?: string };
  subject?: { reference?: string };
  requester?: { reference?: string };
  authoredOn?: string;
  dosageInstruction?: { text?: string }[];
  note?: { text?: string }[];
  [key: string]: any;
}

const BASE_URL = '/api/fhir';

const fhirService = {
  // CarePlan por id de recomendación
  async getCarePlan(recomendacionId: string): Promise<FhirCarePlan> {
    const resp = await axios.get<FhirCarePlan>(
      `${BASE_URL}/CarePlan/${recomendacionId}`,
      { headers: { Accept: 'application/json' } }
    );
    return resp.data;
  },

  // MedicationRequest por paciente
  async getMedicationRequestsByPatient(pacienteId: string): Promise<FhirMedicationRequest[]> {
    const resp = await axios.get<FhirMedicationRequest[]>(
      `${BASE_URL}/MedicationRequest`,
      {
        params: { patient: pacienteId },
        headers: { Accept: 'application/json' },
      }
    );
    return resp.data;
  },
};

export default fhirService;