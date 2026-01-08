// frontend/src/services/fhirService.ts
import axios from 'axios';

export interface FhirPatient {
  resourceType: 'Patient';
  id: string;
  identifier?: { system?: string; value?: string }[];
  name?: { text?: string; family?: string; given?: string[] }[];
  gender?: string;
  birthDate?: string;
  [key: string]: any;
}

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

export interface FhirDetectedIssue {
  resourceType: 'DetectedIssue';
  id: string;
  status?: string;
  severity?: string;
  detail?: string;
  code?: { text?: string };
  patient?: { reference?: string };
  identifiedDateTime?: string;
  [key: string]: any;
}

export interface FhirObservation {
  resourceType: 'Observation';
  id: string;
  status?: string;
  category?: { coding?: { code?: string; display?: string }[]; text?: string }[];
  code?: { text?: string };
  subject?: { reference?: string };
  effectiveDateTime?: string;
  note?: { text?: string }[];
  [key: string]: any;
}

const BASE_URL = '/api/fhir';

const fhirService = {
  // Patient
  async getPatient(pacienteId: string): Promise<FhirPatient> {
    const resp = await axios.get<FhirPatient>(
      `${BASE_URL}/Patient/${pacienteId}`,
      { headers: { Accept: 'application/json' } }
    );
    return resp.data;
  },

  // CarePlan por id de recomendación
  async getCarePlan(recomendacionId: string): Promise<FhirCarePlan> {
    const resp = await axios.get<FhirCarePlan>(
      `${BASE_URL}/CarePlan/${recomendacionId}`,
      { headers: { Accept: 'application/json' } }
    );
    return resp.data;
  },

  // CarePlans por paciente
  async getCarePlansByPatient(pacienteId: string): Promise<FhirCarePlan[]> {
    const resp = await axios.get<FhirCarePlan[]>(
      `${BASE_URL}/CarePlan`,
      {
        params: { patient: pacienteId },
        headers: { Accept: 'application/json' },
      }
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

  // DetectedIssue (interacciones) por paciente
  async getDetectedIssuesByPatient(pacienteId: string): Promise<FhirDetectedIssue[]> {
    const resp = await axios.get<FhirDetectedIssue[]>(
      `${BASE_URL}/DetectedIssue`,
      {
        params: { patient: pacienteId },
        headers: { Accept: 'application/json' },
      }
    );
    return resp.data;
  },

  // Observation (anomalias) por paciente
  async getObservationsByPatient(pacienteId: string): Promise<FhirObservation[]> {
    const resp = await axios.get<FhirObservation[]>(
      `${BASE_URL}/Observation`,
      {
        params: { patient: pacienteId },
        headers: { Accept: 'application/json' },
      }
    );
    return resp.data;
  },
};

export default fhirService;