import React, { useEffect, useState } from 'react';
import { Search, UserPlus, Shield, Trash2, CheckCircle, XCircle } from 'lucide-react';
import securityService, { Role } from '../../services/securityService';
import usuariosService from '../../services/usuariosService';

interface Usuario {
  id: string;
  nombre_completo: string;
  email: string;
  username: string;
  activo: boolean;
  created_at: string;
}

const GestionUsuarios: React.FC = () => {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<Usuario | null>(null);
  const [userRoles, setUserRoles] = useState<Role[]>([]);
  const [showRoleDialog, setShowRoleDialog] = useState(false);
  const [selectedRoleId, setSelectedRoleId] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    nombre_completo: '',
    rol: 'medico',
    especialidad: '',
    cedula_profesional: ''
  });

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [usuariosData, rolesData] = await Promise.all([
        usuariosService.getUsuarios(),
        securityService.getRoles()
      ]);
      setUsuarios(usuariosData);
      setRoles(rolesData);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const cargarRolesUsuario = async (usuarioId: string) => {
    try {
      const rolesData = await securityService.getUserRoles(usuarioId);
      setUserRoles(rolesData);
    } catch (error) {
      console.error('Error al cargar roles del usuario:', error);
    }
  };

  const handleVerRoles = async (usuario: Usuario) => {
    setSelectedUser(usuario);
    await cargarRolesUsuario(usuario.id);
    setShowRoleDialog(true);
  };

  const handleAsignarRol = async () => {
    if (!selectedUser || !selectedRoleId) return;

    try {
      await securityService.assignRoleToUser(selectedUser.id, selectedRoleId);
      await cargarRolesUsuario(selectedUser.id);
      setSelectedRoleId('');
      alert('Rol asignado exitosamente');
    } catch (error) {
      console.error('Error al asignar rol:', error);
      alert('Error al asignar rol');
    }
  };

  const handleRemoverRol = async (roleId: string) => {
    if (!selectedUser) return;

    if (!confirm('¿Estás seguro de remover este rol?')) return;

    try {
      await securityService.removeRoleFromUser(selectedUser.id, roleId);
      await cargarRolesUsuario(selectedUser.id);
      alert('Rol removido exitosamente');
    } catch (error) {
      console.error('Error al remover rol:', error);
      alert('Error al remover rol');
    }
  };

  const handleCrearUsuario = async () => {
    if (!newUser.email || !newUser.password || !newUser.nombre_completo) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      await usuariosService.createUsuario(newUser);
      await cargarDatos();
      setShowCreateDialog(false);
      setNewUser({
        email: '',
        password: '',
        nombre_completo: '',
        rol: 'medico',
        especialidad: '',
        cedula_profesional: ''
      });
      alert('Usuario creado exitosamente');
    } catch (error: any) {
      console.error('Error al crear usuario:', error);
      alert(error.response?.data?.detail || 'Error al crear usuario');
    }
  };

  const usuariosFiltrados = usuarios.filter(u =>
    u.nombre_completo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const rolesDisponibles = roles.filter(r => 
    !userRoles.some(ur => ur.id === r.id)
  );

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
          <h2 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h2>
          <p className="text-sm text-gray-500 mt-1">
            {usuarios.length} usuarios registrados
          </p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <UserPlus className="h-4 w-4 mr-2" />
          Nuevo Usuario
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Buscar por nombre, email o username..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        />
      </div>

      {/* Users Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Usuario
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha Registro
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usuariosFiltrados.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center">
                  <div className="text-gray-500">
                    <p className="text-lg font-medium">No se encontraron usuarios</p>
                    <p className="text-sm mt-1">
                      {searchTerm ? 'Intenta con otro término de búsqueda' : 'Crea el primer usuario con el botón "Nuevo Usuario"'}
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              usuariosFiltrados.map((usuario) => (
                <tr key={usuario.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center">
                      <span className="text-indigo-600 font-medium text-sm">
                        {usuario.nombre_completo.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {usuario.nombre_completo}
                      </div>
                      <div className="text-sm text-gray-500">
                        @{usuario.username}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{usuario.email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {usuario.activo ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Activo
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      <XCircle className="h-3 w-3 mr-1" />
                      Inactivo
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(usuario.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleVerRoles(usuario)}
                    className="text-indigo-600 hover:text-indigo-900 inline-flex items-center"
                  >
                    <Shield className="h-4 w-4 mr-1" />
                    Roles
                  </button>
                </td>
              </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create User Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  Crear Nuevo Usuario
                </h3>
                <button
                  onClick={() => setShowCreateDialog(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Nombre Completo *
                </label>
                <input
                  type="text"
                  value={newUser.nombre_completo}
                  onChange={(e) => setNewUser({ ...newUser, nombre_completo: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Dr. Juan Pérez"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Email *
                </label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="juan.perez@hospital.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Contraseña *
                </label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Rol *
                </label>
                <select
                  value={newUser.rol}
                  onChange={(e) => setNewUser({ ...newUser, rol: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  <option value="medico">Médico</option>
                  <option value="enfermero">Enfermero</option>
                  <option value="administrativo">Administrativo</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Especialidad
                </label>
                <select
                  value={newUser.especialidad}
                  onChange={(e) => setNewUser({ ...newUser, especialidad: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  <option value="">Seleccionar especialidad...</option>
                  <option value="Cardiología">Cardiología</option>
                  <option value="Dermatología">Dermatología</option>
                  <option value="Endocrinología">Endocrinología</option>
                  <option value="Gastroenterología">Gastroenterología</option>
                  <option value="Geriatría">Geriatría</option>
                  <option value="Ginecología">Ginecología</option>
                  <option value="Hematología">Hematología</option>
                  <option value="Medicina General">Medicina General</option>
                  <option value="Medicina Interna">Medicina Interna</option>
                  <option value="Nefrología">Nefrología</option>
                  <option value="Neumología">Neumología</option>
                  <option value="Neurología">Neurología</option>
                  <option value="Oftalmología">Oftalmología</option>
                  <option value="Oncología">Oncología</option>
                  <option value="Ortopedia">Ortopedia</option>
                  <option value="Otorrinolaringología">Otorrinolaringología</option>
                  <option value="Pediatría">Pediatría</option>
                  <option value="Psiquiatría">Psiquiatría</option>
                  <option value="Radiología">Radiología</option>
                  <option value="Reumatología">Reumatología</option>
                  <option value="Traumatología">Traumatología</option>
                  <option value="Urología">Urología</option>
                  <option value="Otra">Otra</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Cédula Profesional
                </label>
                <input
                  type="text"
                  value={newUser.cedula_profesional}
                  onChange={(e) => setNewUser({ ...newUser, cedula_profesional: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="1234567"
                />
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
                onClick={handleCrearUsuario}
                className="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Crear Usuario
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Role Management Dialog */}
      {showRoleDialog && selectedUser && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  Roles de {selectedUser.nombre_completo}
                </h3>
                <button
                  onClick={() => setShowRoleDialog(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>

            <div className="px-6 py-4 space-y-6">
              {/* Current Roles */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3">
                  Roles Actuales ({userRoles.length})
                </h4>
                {userRoles.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">
                    Este usuario no tiene roles asignados
                  </p>
                ) : (
                  <div className="space-y-2">
                    {userRoles.map((role) => (
                      <div
                        key={role.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {role.nombre}
                          </div>
                          <div className="text-xs text-gray-500">
                            {role.descripcion}
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoverRol(role.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Assign New Role */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3">
                  Asignar Nuevo Rol
                </h4>
                <div className="flex space-x-3">
                  <select
                    value={selectedRoleId}
                    onChange={(e) => setSelectedRoleId(e.target.value)}
                    className="flex-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Seleccionar rol...</option>
                    {rolesDisponibles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.nombre} - {role.descripcion}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleAsignarRol}
                    disabled={!selectedRoleId}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <UserPlus className="h-4 w-4 mr-2" />
                    Asignar
                  </button>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <button
                onClick={() => setShowRoleDialog(false)}
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

export default GestionUsuarios;
