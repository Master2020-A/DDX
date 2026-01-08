import api from './api';

export interface Role {
  id: string;
  nombre: string;
  codigo: string;
  descripcion: string;
  nivel: number;
  activo: boolean;
  es_sistema: boolean;
  created_at: string;
}

export interface Permission {
  id: string;
  nombre: string;
  codigo: string;
  descripcion: string;
  modulo: string;
  recurso: string;
  accion: string;
  activo: boolean;
}

export interface UserRole {
  usuario_id: string;
  role_id: string;
  role: Role;
  created_at: string;
}

export interface AuditLog {
  id: string;
  usuario_id: string;
  accion: string;
  recurso: string;
  recurso_id: string;
  descripcion: string;
  datos_anteriores: any;
  datos_nuevos: any;
  ip_address: string;
  user_agent: string;
  metodo_http: string;
  endpoint: string;
  exitoso: boolean;
  codigo_estado: number;
  mensaje_error: string;
  created_at: string;
}

export interface UserSession {
  id: string;
  usuario_id: string;
  session_token: string;
  ip_address: string;
  user_agent: string;
  device_info: any;
  location: string;
  activa: boolean;
  revocada: boolean;
  created_at: string;
  last_activity_at: string;
  expires_at: string;
}

export interface SecurityDashboard {
  total_usuarios: number;
  usuarios_con_2fa: number;
  sesiones_activas: number;
  acciones_ultimo_dia: number;
  acciones_fallidas_ultimo_dia: number;
  roles: Record<string, number>;
}

export interface TwoFactorSetup {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

const securityService = {
  // ==================== ROLES ====================
  
  async getRoles(): Promise<Role[]> {
    const response = await api.get('/security/roles');
    return response.data;
  },

  async getRoleById(roleId: string): Promise<Role> {
    const response = await api.get(`/security/roles/${roleId}`);
    return response.data;
  },

  async createRole(data: {
    nombre: string;
    codigo: string;
    descripcion?: string;
    nivel?: number;
  }): Promise<Role> {
    const response = await api.post('/security/roles', data);
    return response.data;
  },

  async updateRole(roleId: string, data: Partial<Role>): Promise<Role> {
    const response = await api.put(`/security/roles/${roleId}`, data);
    return response.data;
  },

  async deleteRole(roleId: string): Promise<void> {
    await api.delete(`/security/roles/${roleId}`);
  },

  // ==================== PERMISSIONS ====================

  async getPermissions(): Promise<Permission[]> {
    const response = await api.get('/security/permissions');
    return response.data;
  },

  async getRolePermissions(roleId: string): Promise<Permission[]> {
    const response = await api.get(`/security/roles/${roleId}/permissions`);
    return response.data;
  },

  async assignPermissionToRole(roleId: string, permissionId: string): Promise<void> {
    await api.post(`/security/roles/${roleId}/permissions`, { permission_id: permissionId });
  },

  async removePermissionFromRole(roleId: string, permissionId: string): Promise<void> {
    await api.delete(`/security/roles/${roleId}/permissions/${permissionId}`);
  },

  // ==================== USER ROLES ====================

  async getUserRoles(usuarioId: string): Promise<Role[]> {
    const response = await api.get(`/security/users/${usuarioId}/roles`);
    return response.data;
  },

  async getUserPermissions(usuarioId: string): Promise<{ permissions: string[] }> {
    const response = await api.get(`/security/users/${usuarioId}/permissions`);
    return response.data;
  },

  async assignRoleToUser(usuarioId: string, roleId: string): Promise<void> {
    await api.post(`/security/users/${usuarioId}/roles`, { role_id: roleId });
  },

  async removeRoleFromUser(usuarioId: string, roleId: string): Promise<void> {
    await api.delete(`/security/users/${usuarioId}/roles/${roleId}`);
  },

  // ==================== AUDIT LOGS ====================

  async getUserAuditLogs(
    usuarioId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<{ total: number; logs: AuditLog[] }> {
    const response = await api.get(`/security/audit/user/${usuarioId}`, {
      params: { limit, offset }
    });
    return response.data;
  },

  async getResourceAuditLogs(
    recurso: string,
    recursoId: string
  ): Promise<AuditLog[]> {
    const response = await api.get(`/security/audit/resource/${recurso}/${recursoId}`);
    return response.data;
  },

  async getRecentAuditLogs(
    limit: number = 100,
    offset: number = 0
  ): Promise<{ total: number; logs: AuditLog[] }> {
    const response = await api.get('/security/audit/logs', {
      params: { limit, offset }
    });
    return response.data;
  },

  // ==================== SESSIONS ====================

  async getUserSessions(usuarioId: string): Promise<UserSession[]> {
    const response = await api.get(`/security/sessions/user/${usuarioId}`);
    return response.data;
  },

  async getMySessions(): Promise<{ total: number; sessions: UserSession[] }> {
    const response = await api.get('/security/sessions/me');
    return response.data;
  },

  async revokeSession(sessionId: string, motivo?: string): Promise<void> {
    await api.post(`/security/sessions/${sessionId}/revoke`, { motivo });
  },

  async revokeAllSessions(): Promise<void> {
    await api.post('/security/sessions/revoke-all');
  },

  // ==================== 2FA ====================

  async setup2FA(): Promise<TwoFactorSetup> {
    const response = await api.post('/security/2fa/setup');
    return response.data;
  },

  async verify2FA(token: string): Promise<{ message: string; enabled: boolean }> {
    const response = await api.post('/security/2fa/verify', { token });
    return response.data;
  },

  async disable2FA(): Promise<void> {
    await api.post('/security/2fa/disable');
  },

  async get2FAStatus(): Promise<{ enabled: boolean; method: string }> {
    const response = await api.get('/security/2fa/status');
    return response.data;
  },

  // ==================== DASHBOARD ====================

  async getDashboard(): Promise<SecurityDashboard> {
    const response = await api.get('/security/admin/dashboard');
    return response.data;
  },

  // ==================== INITIALIZATION ====================

  async initializeSecurity(): Promise<{ message: string; permisos_creados: number; roles_creados: number }> {
    const response = await api.post('/security/initialize');
    return response.data;
  }
};

export default securityService;
