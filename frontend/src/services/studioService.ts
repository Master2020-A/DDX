// src/services/studioService.ts
import api from "@/lib/api";

export interface StudioModule {
  id: string;
  module_id: string;
  name: string;
  description?: string | null;
  version: string;
  status: string;
  icon?: string | null;
  color?: string | null;
  category?: string | null;
  created_at: string;
  updated_at: string;
}

export async function listModules(): Promise<StudioModule[]> {
  const res = await api.get("/studio/modules");
  return res.data;
}

export async function createModule(payload: any): Promise<StudioModule> {
  const res = await api.post("/studio/modules", payload);
  return res.data;
}

export async function getModule(moduleId: string): Promise<StudioModule> {
  const res = await api.get(`/studio/modules/${moduleId}`);
  return res.data;
}

export async function updateModule(moduleId: string, payload: any): Promise<StudioModule> {
  const res = await api.put(`/studio/modules/${moduleId}`, payload);
  return res.data;
}

export async function deleteModule(moduleId: string): Promise<{ message: string }> {
  const res = await api.delete(`/studio/modules/${moduleId}`);
  return res.data;
}

export async function previewModule(moduleId: string): Promise<any> {
  const res = await api.post(`/studio/modules/${moduleId}/preview`);
  return res.data;
}

export async function deployModule(moduleId: string): Promise<any> {
  const res = await api.post(`/studio/modules/${moduleId}/deploy`);
  return res.data;
}

export async function getCategories(): Promise<any> {
  const res = await api.get("/studio/categories");
  return res.data;
}

export async function getFieldTypes(): Promise<any> {
  const res = await api.get("/studio/field-types");
  return res.data;
}