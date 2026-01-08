import React, { useEffect, useState } from 'react';
import { Key, Plus, CheckSquare, Square } from 'lucide-react';
import securityService, { Role, Permission } from '../../services/securityService';

const GestionRoles: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [rolePermissions, setRolePermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [showPermissionsDialog, setShowPermissionsDialog] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newRole, setNewRole] = useState({
    nombre: '',
    codigo: '',
    descripcion: '',
    nivel: 1
  });

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [rolesData, permissionsData] = await Promise.all([
        securityService.getRoles(),
        securityService.getPermissions()
      ]);
      setRoles(rolesData);
      setPermissions(permissionsData);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const cargarPermisosRol = async (roleId: string) => {
    try {
      const perms = await securityService.getRolePermissions(roleId);
      setRolePermissions(perms);
    } catch (error) {
      console.error('Error al cargar permisos del rol:', error);
    }
  };

  const handleVerPermisos = async (role: Role) => {
    setSelectedRole(role);
    await cargarPermisosRol(role.id);
    setShowPermissionsDialog(true);
  };

  const handleTogglePermission = async (permission: Permission) => {
    if (!selectedRole) return;

    const hasPermission = rolePermissions.some(p => p.id === permission.id);

    try {
      if (hasPermission) {
        await securityService.removePermissionFromRole(selectedRole.id, permission.id);
      } else {
        await securityService.assignPermissionToRole(selectedRole.id, permission.id);
      }
      await cargarPermisosRol(selectedRole.id);
    } catch (error) {
      console.error('Error al cambiar permiso:', error);
      alert('Error al cambiar permiso');
    }
  };

  const handleCrearRol = async () => {
    if (!newRole.nombre || !newRole.codigo || !newRole.descripcion) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      await securityService.createRole(newRole);
      await cargarDatos();
      setShowCreateDialog(false);
      setNewRole({
        nombre: '',
        codigo: '',
        descripcion: '',
        nivel: 1
      });
      alert('Rol creado exitosamente');
    } catch (error: any) {
      console.error('Error al crear rol:', error);
      alert(error.response?.data?.detail || 'Error al crear rol');
    }
  };

  const permissionsByModule = permissions.reduce((acc, perm) => {
    if (!acc[perm.modulo]) {
      acc[perm.modulo] = [];
    }
    acc[perm.modulo].push(perm);
    return acc;
  }, {} as Record<string, Permission[]>);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gestión de Roles y Permisos</h2>
          <p className="text-sm text-gray-500 mt-1">
            {roles.length} roles • {permissions.length} permisos
          </p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Rol
        </button>
      </div>

      {/* Roles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {roles.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="text-gray-500">
              <p className="text-lg font-medium">No se encontraron roles</p>
              <p className="text-sm mt-1">Crea el primer rol con el botón "Nuevo Rol"</p>
            </div>
          </div>
        ) : (
          roles.map((role) => (
          <div
            key={role.id}
            className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  role.codigo === 'admin' ? 'bg-red-100' :
                  role.codigo === 'medico' ? 'bg-blue-100' :
                  role.codigo === 'enfermero' ? 'bg-green-100' :
                  'bg-yellow-100'
                }`}>
                  <Key className={`h-6 w-6 ${
                    role.codigo === 'admin' ? 'text-red-600' :
                    role.codigo === 'medico' ? 'text-blue-600' :
                    role.codigo === 'enfermero' ? 'text-green-600' :
                    'text-yellow-600'
                  }`} />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {role.nombre}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Nivel {role.nivel}
                  </p>
                </div>
              </div>
              {role.es_sistema && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Sistema
                </span>
              )}
            </div>

            <p className="mt-4 text-sm text-gray-600">
              {role.descripcion}
            </p>

            <div className="mt-4 flex items-center justify-between">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                role.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {role.activo ? 'Activo' : 'Inactivo'}
              </span>
              <button
                onClick={() => handleVerPermisos(role)}
                className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
              >
                Ver Permisos →
              </button>
            </div>
          </div>
          ))
        )}
      </div>

      {/* Create Role Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  Crear Nuevo Rol
                </h3>
                <button
                  onClick={() => setShowCreateDialog(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Nombre del Rol *
                </label>
                <input
                  type="text"
                  value={newRole.nombre}
                  onChange={(e) => setNewRole({ ...newRole, nombre: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Especialista"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Código *
                </label>
                <input
                  type="text"
                  value={newRole.codigo}
                  onChange={(e) => setNewRole({ ...newRole, codigo: e.target.value.toLowerCase() })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="especialista"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Descripción *
                </label>
                <textarea
                  value={newRole.descripcion}
                  onChange={(e) => setNewRole({ ...newRole, descripcion: e.target.value })}
                  rows={3}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Descripción del rol y sus responsabilidades"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Nivel de Acceso *
                </label>
                <select
                  value={newRole.nivel}
                  onChange={(e) => setNewRole({ ...newRole, nivel: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  <option value={0}>0 - Administrador</option>
                  <option value={1}>1 - Alto</option>
                  <option value={2}>2 - Medio</option>
                  <option value={3}>3 - Bajo</option>
                </select>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateDialog(false)}
                className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Cancelar
              </button>
              <button
                onClick={handleCrearRol}
                className="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Crear Rol
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Permissions Dialog */}
      {showPermissionsDialog && selectedRole && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    Permisos de {selectedRole.nombre}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {rolePermissions.length} de {permissions.length} permisos asignados
                  </p>
                </div>
                <button
                  onClick={() => setShowPermissionsDialog(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="px-6 py-4 space-y-6">
              {Object.entries(permissionsByModule).map(([modulo, perms]) => (
                <div key={modulo}>
                  <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-3">
                    {modulo}
                  </h4>
                  <div className="space-y-2">
                    {perms.map((permission) => {
                      const hasPermission = rolePermissions.some(p => p.id === permission.id);
                      return (
                        <div
                          key={permission.id}
                          className={`flex items-center justify-between p-3 rounded-lg border-2 cursor-pointer transition-colors ${
                            hasPermission
                              ? 'border-indigo-500 bg-indigo-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => handleTogglePermission(permission)}
                        >
                          <div className="flex items-center space-x-3">
                            {hasPermission ? (
                              <CheckSquare className="h-5 w-5 text-indigo-600" />
                            ) : (
                              <Square className="h-5 w-5 text-gray-400" />
                            )}
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {permission.nombre}
                              </div>
                              <div className="text-xs text-gray-500">
                                {permission.codigo}
                              </div>
                            </div>
                          </div>
                          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                            permission.accion === 'view' ? 'bg-blue-100 text-blue-800' :
                            permission.accion === 'create' ? 'bg-green-100 text-green-800' :
                            permission.accion === 'edit' ? 'bg-yellow-100 text-yellow-800' :
                            permission.accion === 'delete' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {permission.accion}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 sticky bottom-0">
              <button
                onClick={() => setShowPermissionsDialog(false)}
                className="w-full inline-flex justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GestionRoles;
