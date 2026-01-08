import api from "@/lib/api";

export type Workflow = {
  id: string;
  workflow_id: string;
  name: string;
  description?: string | null;
  category?: string | null;
  status: string;
  version?: string;
  nodes: any[];
  edges: any[];
  config?: any;
  variables?: any;
  icon?: string | null;
  color?: string | null;
  tags?: string[] | null;
  created_at?: string;
  updated_at?: string;
};

export type Execution = {
  id: string;
  workflow_id: string;
  status: string;
  input_data: any;
  output_data?: any;
  error?: string | null;
  started_at?: string;
  completed_at?: string | null;
};

export async function listWorkflows(): Promise<Workflow[]> {
  // backend: GET /api/workflows
  const res = await api.get("/workflows");
  return res.data;
}

export async function createWorkflow(payload: any): Promise<Workflow> {
  const res = await api.post("/workflows", payload);
  return res.data;
}

export async function getWorkflow(workflowId: string): Promise<Workflow> {
  const res = await api.get(`/workflows/${workflowId}`);
  return res.data;
}

export async function updateWorkflow(workflowId: string, payload: any): Promise<Workflow> {
  const res = await api.put(`/workflows/${workflowId}`, payload);
  return res.data;
}

export async function deleteWorkflow(workflowId: string): Promise<any> {
  const res = await api.delete(`/workflows/${workflowId}`);
  return res.data;
}

export async function executeWorkflow(workflowId: string, input_data: any): Promise<Execution> {
  const res = await api.post(`/workflows/${workflowId}/execute`, { input_data });
  return res.data;
}

export async function listExecutions(workflowId: string, limit = 50): Promise<Execution[]> {
  const res = await api.get(`/workflows/${workflowId}/executions`, { params: { limit } });
  return res.data;
}

export async function getExecution(executionId: string): Promise<Execution> {
  const res = await api.get(`/workflows/executions/${executionId}`);
  return res.data;
}

export async function listNodeTypes(): Promise<any> {
  const res = await api.get(`/workflows/node-types`);
  return res.data;
}

export async function listAgentModels(): Promise<any> {
  const res = await api.get(`/workflows/agent-models`);
  return res.data;
}

export async function listTemplates(category?: string): Promise<any> {
  const res = await api.get(`/workflows/templates`, { params: category ? { category } : undefined });
  return res.data;
}

export async function useTemplate(templateId: string, workflow_id: string, name: string): Promise<Workflow> {
  const res = await api.post(`/workflows/templates/${templateId}/use`, { workflow_id, name });
  return res.data;
}

export async function listAgents(workflowId: string): Promise<any[]> {
  const res = await api.get(`/workflows/${workflowId}/agents`);
  return res.data;
}

export async function createAgent(workflowId: string, payload: any): Promise<any> {
  const res = await api.post(`/workflows/${workflowId}/agents`, payload);
  return res.data;
}