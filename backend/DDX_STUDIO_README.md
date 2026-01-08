# DDX Studio - Constructor Visual No-Code

## 🎯 Descripción

DDX Studio es un **constructor visual no-code** completamente funcional que permite crear módulos personalizados para el sistema DDX sin escribir código manualmente. Los módulos generados son **100% funcionales** y se integran automáticamente al sistema.

## ✨ Características Principales

### 🔧 Generación Automática de Código
- **Modelos SQLAlchemy**: Genera clases de modelos con todos los campos y relaciones
- **Endpoints FastAPI**: Crea APIs REST completas con CRUD automático
- **Componentes React**: Genera interfaces de usuario funcionales
- **Migraciones SQL**: Crea y ejecuta automáticamente las tablas en PostgreSQL

### 📦 Despliegue Automático
- Escribe archivos físicos en el proyecto
- Ejecuta migraciones SQL automáticamente
- Registra rutas dinámicamente sin reiniciar el servidor
- Carga módulos al iniciar la aplicación

### 🎨 Interfaz Visual Completa
- Constructor de modelos con campos personalizables
- Configuración de tipos de datos, validaciones e índices
- Preview de código antes de desplegar
- Gestión de módulos activos/inactivos

## 🚀 Cómo Usar

### 1. Acceder a DDX Studio

Navega a: **Dashboard → DDX Studio** (`/ddx-studio`)

### 2. Crear un Nuevo Módulo

1. Click en **"Nuevo Módulo"**
2. Completa la información básica:
   - **ID del Módulo**: Identificador único (solo minúsculas, números y guiones)
   - **Nombre**: Nombre descriptivo del módulo
   - **Descripción**: Descripción opcional
   - **Categoría**: Clínico, Administrativo, Laboratorio, etc.
   - **Color**: Color de identificación

### 3. Construir Modelos

Para cada modelo que necesites:

1. **Información del Modelo**:
   - Nombre del Modelo (ej: `Vacuna`)
   - Nombre de Tabla (ej: `vacunas`)
   - Descripción opcional

2. **Agregar Campos**:
   - Nombre del campo (ej: `nombre_vacuna`)
   - Tipo de dato: string, text, integer, float, boolean, date, datetime, uuid, json
   - Etiqueta para formularios
   - Opciones:
     - ✅ Requerido
     - ✅ Único
     - ✅ Indexado

3. Click en **"Agregar Campo"** para cada campo

4. Click en **"Agregar Modelo al Módulo"** cuando termines

### 4. Desplegar el Módulo

1. Click en el botón **"Desplegar"** (▶️) del módulo
2. El sistema automáticamente:
   - Genera el código de modelos, endpoints y componentes
   - Escribe los archivos en las carpetas correspondientes
   - Ejecuta las migraciones SQL para crear las tablas
   - Registra las rutas en el servidor

3. El módulo cambia a estado **"Activo"** ✅

### 5. Usar el Módulo

Los endpoints generados están disponibles en:
```
/api/generated/{nombre_tabla}
```

Ejemplo de endpoints generados:
- `POST /api/generated/vacunas` - Crear registro
- `GET /api/generated/vacunas` - Listar registros
- `GET /api/generated/vacunas/{id}` - Obtener por ID
- `PUT /api/generated/vacunas/{id}` - Actualizar
- `DELETE /api/generated/vacunas/{id}` - Eliminar

## 📂 Estructura de Archivos Generados

```
backend/
├── app/
│   ├── models/
│   │   └── generated/
│   │       ├── __init__.py
│   │       └── vacuna.py          # Modelo SQLAlchemy
│   └── api/
│       └── generated/
│           ├── __init__.py
│           └── vacuna.py          # Endpoints FastAPI

frontend/
└── src/
    └── pages/
        └── generated/
            └── VacunaPage.tsx     # Componente React
```

## 🔍 Preview de Código

Antes de desplegar, puedes ver el código que se generará:

1. Click en el botón **"👁️"** (ojo) del módulo
2. Revisa:
   - Código del modelo (SQLAlchemy)
   - Código del endpoint (FastAPI)
   - Código del componente (React)
   - SQL de migración

## 🛠️ Gestión de Módulos

### Desactivar un Módulo
- Click en **"Desactivar"** para eliminar los archivos generados
- La definición del módulo se mantiene en la base de datos
- Puedes volver a desplegarlo después

### Eliminar un Módulo
- Click en **"🗑️"** (papelera) para eliminar permanentemente
- Se eliminan los archivos generados
- Se elimina la definición de la base de datos
- ⚠️ **Las tablas SQL NO se eliminan** por seguridad

## 📊 Tipos de Datos Disponibles

| Tipo | SQL | Python | TypeScript | Uso |
|------|-----|--------|------------|-----|
| `string` | VARCHAR(255) | str | string | Texto corto |
| `text` | TEXT | str | string | Texto largo |
| `integer` | INTEGER | int | number | Números enteros |
| `float` | FLOAT | float | number | Decimales |
| `boolean` | BOOLEAN | bool | boolean | Verdadero/Falso |
| `date` | DATE | str | string | Solo fecha |
| `datetime` | TIMESTAMP | str | string | Fecha y hora |
| `uuid` | UUID | UUID | string | Identificador único |
| `json` | JSONB | dict | any | Datos JSON |

## 🎯 Ejemplo Completo: Módulo de Vacunas

### Paso 1: Crear Módulo
```
ID: vacunas-covid
Nombre: Vacunas COVID-19
Descripción: Gestión de vacunas contra COVID-19
Categoría: clinical
```

### Paso 2: Crear Modelo
```
Nombre: Vacuna
Tabla: vacunas_covid
```

### Paso 3: Agregar Campos
```
1. nombre_vacuna (string, requerido)
2. fabricante (string, requerido)
3. lote (string, único, indexado)
4. fecha_aplicacion (datetime, requerido)
5. dosis_numero (integer, requerido)
6. paciente_id (uuid, requerido, indexado)
7. efectos_adversos (text, opcional)
8. certificado_emitido (boolean, default: false)
```

### Paso 4: Desplegar

El sistema genera automáticamente:

**Modelo** (`app/models/generated/vacuna.py`):
```python
class Vacuna(Base):
    __tablename__ = "vacunas_covid"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_vacuna = Column(String(255), nullable=False)
    fabricante = Column(String(255), nullable=False)
    lote = Column(String(255), unique=True, index=True)
    # ... más campos
```

**Endpoints** (`app/api/generated/vacuna.py`):
```python
@router.post("/vacunas_covid")
async def create_vacuna(data: VacunaCreate, db: AsyncSession = Depends(get_db)):
    # CRUD completo generado automáticamente
```

**Tabla SQL**:
```sql
CREATE TABLE IF NOT EXISTS vacunas_covid (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_vacuna VARCHAR(255) NOT NULL,
    fabricante VARCHAR(255) NOT NULL,
    lote VARCHAR(255) UNIQUE,
    -- ... más campos
);
CREATE INDEX IF NOT EXISTS idx_vacunas_covid_lote ON vacunas_covid(lote);
```

## 🔄 Carga Dinámica de Módulos

Los módulos se cargan automáticamente al iniciar el servidor:

```python
# En app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.module_deployer import ModuleDeployer
    deployer = ModuleDeployer()
    loaded = deployer.load_generated_routes(app)
    logger.info(f"✅ Cargados {len(loaded)} módulos generados")
```

## 🔐 Seguridad

- Todos los endpoints requieren autenticación por defecto
- Los módulos solo pueden ser creados por usuarios autenticados
- Las migraciones SQL se ejecutan con validación
- Los archivos se escriben en directorios controlados

## 🐛 Troubleshooting

### El módulo no aparece después de desplegar
- Reinicia el servidor backend para cargar las rutas
- Verifica los logs del servidor para errores

### Error al ejecutar migración SQL
- Verifica que la tabla no exista ya
- Revisa los permisos de la base de datos
- Consulta los logs de despliegue en la base de datos

### Los endpoints no responden
- Verifica que el módulo esté en estado "active"
- Revisa la documentación de la API en `/docs`
- Busca las rutas en `/api/generated/{tabla}`

## 📝 Notas Importantes

1. **Campos Automáticos**: Todos los modelos incluyen automáticamente:
   - `id` (UUID, primary key)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

2. **Reinicio del Servidor**: Aunque los módulos se cargan dinámicamente, se recomienda reiniciar el servidor después de desplegar para asegurar la carga completa.

3. **Backup**: Antes de eliminar un módulo, asegúrate de hacer backup de los datos si son importantes.

4. **Validaciones**: Puedes agregar validaciones personalizadas editando el código generado.

## 🎓 Mejores Prácticas

1. **Nombres Descriptivos**: Usa nombres claros para módulos, modelos y campos
2. **Índices**: Agrega índices a campos que usarás en búsquedas frecuentes
3. **Campos Únicos**: Marca como únicos los campos que no deben duplicarse
4. **Preview Primero**: Siempre revisa el código antes de desplegar
5. **Pruebas**: Prueba los endpoints generados en `/docs` antes de usar en producción

## 🚀 Próximas Características

- [ ] Relaciones entre modelos generados
- [ ] Validaciones personalizadas
- [ ] Permisos granulares por endpoint
- [ ] Exportar/Importar definiciones de módulos
- [ ] Versionado de módulos
- [ ] Hot-reload sin reiniciar servidor

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Revisa los logs del servidor
2. Verifica la documentación de la API en `/docs`
3. Consulta el código generado en las carpetas `generated/`

---

**DDX Studio** - Construye módulos personalizados sin escribir código 🎨
