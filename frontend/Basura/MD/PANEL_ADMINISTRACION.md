# 🔐 Panel de Administración - Sistema de Seguridad

## 📋 DESCRIPCIÓN

Panel de administración completo para gestionar usuarios, roles, permisos y auditoría del sistema. Interfaz separada del usuario normal con funcionalidades avanzadas de seguridad.

---

## 🎯 CARACTERÍSTICAS PRINCIPALES

### **1. Dashboard de Seguridad**
- Estadísticas en tiempo real
- Total de usuarios registrados
- Usuarios con 2FA activado
- Sesiones activas
- Acciones fallidas en las últimas 24h
- Distribución de roles con gráficas
- Recomendaciones de seguridad automáticas

### **2. Gestión de Usuarios**
- Lista completa de usuarios del sistema
- Búsqueda por nombre, email o username
- Ver estado (activo/inactivo)
- Asignar/remover roles a usuarios
- Ver permisos efectivos de cada usuario
- Indicadores visuales de estado

### **3. Gestión de Roles y Permisos**
- Vista de todos los roles del sistema
- Permisos organizados por módulo
- Asignar/remover permisos a roles
- Indicadores de roles del sistema
- Niveles de acceso por rol
- Interfaz visual con checkboxes

### **4. Logs de Auditoría**
- Registro completo de todas las acciones
- Filtros por estado (exitoso/fallido)
- Detalles completos de cada acción
- Información de IP, user agent, endpoint
- Datos anteriores y nuevos (diff)
- Paginación para grandes volúmenes
- Búsqueda y exportación

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
frontend/src/
├── pages/
│   └── Admin.tsx                          # Página principal del panel
├── components/admin/
│   ├── DashboardSeguridad.tsx            # Dashboard con estadísticas
│   ├── GestionUsuarios.tsx               # Gestión de usuarios y roles
│   ├── GestionRoles.tsx                  # Gestión de roles y permisos
│   └── LogsAuditoria.tsx                 # Visor de logs de auditoría
└── services/
    └── securityService.ts                # Servicio API de seguridad
```

---

## 🚀 INSTALACIÓN Y CONFIGURACIÓN

### **1. Agregar Ruta al Router**

Edita `src/App.tsx` o tu archivo de rutas:

```typescript
import Admin from './pages/Admin';

// Dentro de tus rutas
<Route path="/admin" element={<Admin />} />
```

### **2. Agregar Enlace en Navegación**

Edita tu componente de navegación (ej: `Navbar.tsx`):

```typescript
import { Settings } from 'lucide-react';

// Solo mostrar para administradores
{currentUser?.rol === 'admin' && (
  <Link
    to="/admin"
    className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
  >
    <Settings className="h-5 w-5" />
    <span>Administración</span>
  </Link>
)}
```

### **3. Proteger Ruta (Opcional)**

Crea un componente de protección de rutas:

```typescript
// src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface Props {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<Props> = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Cargando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (requiredRole && user.rol !== requiredRole) {
    return <Navigate to="/" />;
  }

  return <>{children}</>;
};

// Uso en rutas
<Route
  path="/admin"
  element={
    <ProtectedRoute requiredRole="admin">
      <Admin />
    </ProtectedRoute>
  }
/>
```

---

## 💻 USO DEL PANEL

### **Dashboard de Seguridad**

Al acceder a `/admin`, verás:

1. **Tarjetas de Estadísticas:**
   - Total de usuarios
   - Usuarios con 2FA (porcentaje)
   - Sesiones activas en tiempo real
   - Acciones fallidas (últimas 24h)

2. **Distribución de Roles:**
   - Gráfica de barras con porcentajes
   - Colores por rol (Admin=rojo, Médico=azul, etc.)
   - Conteo de usuarios por rol

3. **Actividad Reciente:**
   - Acciones totales en 24h
   - Acciones exitosas vs fallidas

4. **Recomendaciones:**
   - Alertas si menos del 50% tiene 2FA
   - Alertas de acciones fallidas excesivas
   - Alertas de sesiones múltiples sospechosas

### **Gestión de Usuarios**

**Buscar Usuarios:**
```
1. Usa la barra de búsqueda
2. Filtra por nombre, email o username
3. Los resultados se actualizan en tiempo real
```

**Asignar Rol a Usuario:**
```
1. Click en "Roles" junto al usuario
2. Se abre diálogo con roles actuales
3. Selecciona nuevo rol del dropdown
4. Click "Asignar"
5. El rol aparece en la lista
```

**Remover Rol:**
```
1. En el diálogo de roles del usuario
2. Click en el icono de basura (🗑️) junto al rol
3. Confirma la acción
4. El rol se remueve
```

### **Gestión de Roles y Permisos**

**Ver Permisos de un Rol:**
```
1. Click en "Ver Permisos →" en la tarjeta del rol
2. Se abre diálogo con todos los permisos
3. Permisos organizados por módulo
4. Checkboxes muestran permisos asignados
```

**Asignar/Remover Permiso:**
```
1. En el diálogo de permisos
2. Click en cualquier permiso (checkbox)
3. Se asigna/remueve automáticamente
4. Borde azul indica permiso asignado
5. Borde gris indica permiso no asignado
```

**Permisos por Módulo:**
- **Pacientes:** view, create, edit, delete
- **Consultas:** view, create, edit, delete
- **Diagnósticos:** view, create, edit, delete
- **Hospitalización:** view, create, edit, alta
- **Analytics:** view, export
- **Admin:** users, roles, audit

### **Logs de Auditoría**

**Filtrar Logs:**
```
1. Usa el dropdown "Todos/Exitosos/Fallidos"
2. Los logs se filtran automáticamente
3. Estadísticas se actualizan en tiempo real
```

**Ver Detalle de un Log:**
```
1. Click en el icono de ojo (👁️)
2. Se abre diálogo con información completa:
   - Estado y código HTTP
   - Acción y recurso
   - IP address y user agent
   - Endpoint llamado
   - Datos anteriores (antes del cambio)
   - Datos nuevos (después del cambio)
   - Mensaje de error (si falló)
```

**Navegar entre Páginas:**
```
1. Usa botones "Anterior/Siguiente"
2. Muestra 50 logs por página
3. Indicador de página actual
```

---

## 🎨 COMPONENTES Y PROPS

### **Admin.tsx**
```typescript
// Página principal - No recibe props
<Admin />
```

### **DashboardSeguridad.tsx**
```typescript
// Dashboard de estadísticas - No recibe props
<DashboardSeguridad />
```

### **GestionUsuarios.tsx**
```typescript
// Gestión de usuarios - No recibe props
<GestionUsuarios />
```

### **GestionRoles.tsx**
```typescript
// Gestión de roles y permisos - No recibe props
<GestionRoles />
```

### **LogsAuditoria.tsx**
```typescript
// Visor de logs - No recibe props
<LogsAuditoria />
```

---

## 🔌 API ENDPOINTS UTILIZADOS

### **Dashboard**
```typescript
GET /api/security/dashboard
// Retorna estadísticas generales del sistema
```

### **Usuarios**
```typescript
GET /api/usuarios
// Lista todos los usuarios

GET /api/security/users/{usuario_id}/roles
// Obtiene roles de un usuario

POST /api/security/users/{usuario_id}/roles
// Asigna rol a usuario
Body: { role_id: string }

DELETE /api/security/users/{usuario_id}/roles/{role_id}
// Remueve rol de usuario
```

### **Roles y Permisos**
```typescript
GET /api/security/roles
// Lista todos los roles

GET /api/security/permissions
// Lista todos los permisos

GET /api/security/roles/{role_id}/permissions
// Obtiene permisos de un rol

POST /api/security/roles/{role_id}/permissions
// Asigna permiso a rol
Body: { permission_id: string }

DELETE /api/security/roles/{role_id}/permissions/{permission_id}
// Remueve permiso de rol
```

### **Auditoría**
```typescript
GET /api/security/audit/recent?limit=50&offset=0
// Obtiene logs recientes con paginación

GET /api/security/audit/user/{usuario_id}?limit=50&offset=0
// Obtiene logs de un usuario específico
```

---

## 🎯 CASOS DE USO

### **Caso 1: Nuevo Médico en el Sistema**

```
1. Usuario se registra en el sistema (rol por defecto: ninguno)
2. Administrador accede a /admin
3. Va a "Usuarios"
4. Busca al nuevo usuario por nombre
5. Click en "Roles"
6. Selecciona "Médico" del dropdown
7. Click "Asignar"
8. El usuario ahora tiene permisos médicos
```

### **Caso 2: Crear Rol Personalizado**

```
1. Administrador accede a /admin
2. Va a "Roles y Permisos"
3. (Actualmente solo visualización)
4. Para crear rol nuevo, usar endpoint:
   POST /api/security/roles
   {
     "nombre": "Laboratorista",
     "codigo": "laboratorista",
     "descripcion": "Acceso a laboratorios",
     "nivel": 20
   }
5. Asignar permisos específicos
```

### **Caso 3: Investigar Acción Sospechosa**

```
1. Administrador recibe alerta de acciones fallidas
2. Accede a /admin → "Auditoría"
3. Filtra por "Fallidos"
4. Revisa logs con errores
5. Click en ojo (👁️) para ver detalle
6. Analiza IP, endpoint, mensaje de error
7. Identifica patrón de ataque o error
8. Toma acción (bloquear IP, revisar código, etc.)
```

### **Caso 4: Auditar Cambios en Paciente**

```
1. Administrador necesita ver quién modificó un paciente
2. Accede a /admin → "Auditoría"
3. Busca logs de recurso "paciente"
4. Filtra por recurso_id específico
5. Ve historial completo de cambios
6. Compara datos_anteriores vs datos_nuevos
7. Identifica quién hizo qué cambio y cuándo
```

---

## 🔒 SEGURIDAD Y PERMISOS

### **Acceso al Panel**

El panel de administración debe estar protegido:

```typescript
// Solo usuarios con rol 'admin' pueden acceder
if (currentUser?.rol !== 'admin') {
  return <Navigate to="/" />;
}
```

### **Permisos Requeridos**

Para cada acción en el panel:

| Acción | Permiso Requerido |
|--------|-------------------|
| Ver dashboard | `admin.users` o `admin.audit` |
| Listar usuarios | `admin.users` |
| Asignar roles | `admin.roles` |
| Ver permisos | `admin.roles` |
| Modificar permisos | `admin.roles` |
| Ver logs | `admin.audit` |

### **Auditoría de Acciones del Admin**

Todas las acciones del administrador se registran:

```typescript
// Ejemplo: Al asignar un rol
await securityService.assignRoleToUser(userId, roleId);
// Automáticamente se crea log de auditoría:
{
  accion: "asignar_rol",
  recurso: "usuario",
  recurso_id: userId,
  descripcion: "Asignó rol 'Médico' a usuario Juan Pérez",
  usuario_id: adminId,
  exitoso: true
}
```

---

## 📊 MÉTRICAS Y MONITOREO

### **Métricas Clave**

El dashboard muestra:

1. **Tasa de Adopción 2FA:**
   ```
   (usuarios_con_2fa / total_usuarios) * 100
   ```

2. **Tasa de Éxito de Acciones:**
   ```
   ((acciones_totales - acciones_fallidas) / acciones_totales) * 100
   ```

3. **Sesiones por Usuario:**
   ```
   sesiones_activas / total_usuarios
   ```

4. **Distribución de Roles:**
   ```
   Porcentaje de usuarios por rol
   ```

### **Alertas Automáticas**

El sistema genera alertas cuando:

- ✅ Menos del 50% tiene 2FA → "Considera hacerlo obligatorio"
- ✅ Más de 10 acciones fallidas en 24h → "Revisa seguridad"
- ✅ Más de 2 sesiones por usuario → "Revisa sesiones sospechosas"
- ✅ 100% con 2FA → "¡Excelente seguridad!"

---

## 🎨 PERSONALIZACIÓN

### **Colores por Rol**

Puedes personalizar los colores en `GestionRoles.tsx`:

```typescript
const getRoleColor = (codigo: string) => {
  switch (codigo) {
    case 'admin': return 'bg-red-100 text-red-600';
    case 'medico': return 'bg-blue-100 text-blue-600';
    case 'enfermero': return 'bg-green-100 text-green-600';
    case 'recepcionista': return 'bg-yellow-100 text-yellow-600';
    default: return 'bg-gray-100 text-gray-600';
  }
};
```

### **Límites de Paginación**

Ajusta el límite de logs por página en `LogsAuditoria.tsx`:

```typescript
const [limit] = useState(50); // Cambiar a 100, 200, etc.
```

---

## 🐛 TROUBLESHOOTING

### **Error: "Cannot find module './api'"**

Asegúrate de tener el archivo `src/services/api.ts`:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### **Error: "usuariosService is not defined"**

Crea el servicio de usuarios en `src/services/usuariosService.ts`:

```typescript
import api from './api';

const usuariosService = {
  async getUsuarios() {
    const response = await api.get('/usuarios');
    return response.data;
  }
};

export default usuariosService;
```

### **Los logs no se cargan**

Verifica que el backend esté corriendo y que el endpoint `/api/security/audit/recent` esté disponible.

---

## 📝 PRÓXIMAS MEJORAS

- [ ] Exportar logs a CSV/PDF
- [ ] Gráficas de tendencias temporales
- [ ] Alertas en tiempo real con WebSockets
- [ ] Crear/editar roles desde el frontend
- [ ] Búsqueda avanzada en logs
- [ ] Filtros por fecha en logs
- [ ] Dashboard personalizable
- [ ] Modo oscuro

---

## 🎓 MEJORES PRÁCTICAS

1. **Revisar logs regularmente** - Al menos una vez por semana
2. **Mantener 2FA obligatorio** - Para todos los administradores
3. **Auditar cambios críticos** - Especialmente eliminaciones
4. **Rotar permisos** - Revisar y actualizar cada 3 meses
5. **Monitorear sesiones** - Revocar sesiones inactivas
6. **Documentar cambios** - Mantener registro de modificaciones de roles

---

## 📞 SOPORTE

Para más información:
- Backend: `GUIA_USO_SEGURIDAD.md`
- Endpoints: `http://localhost:8000/docs`
- Módulo completo: `SECURITY_MODULE.md`
