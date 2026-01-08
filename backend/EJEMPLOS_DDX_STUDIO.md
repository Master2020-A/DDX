# Ejemplos de Módulos para DDX Studio

## 📋 Módulos de Ejemplo Listos para Usar

Estos son ejemplos completos de módulos que puedes crear en DDX Studio. Cada uno se integra con el sistema DDX existente usando relaciones con pacientes, usuarios y consultas.

---

## 1. 💉 Módulo de Vacunación COVID-19

### Información del Módulo
- **ID**: `vacunacion-covid`
- **Nombre**: Vacunación COVID-19
- **Descripción**: Registro y seguimiento de vacunas COVID-19 aplicadas a pacientes
- **Categoría**: clinical
- **Color**: #10b981 (verde)

### Modelo: Vacuna

**Nombre del Modelo**: `VacunaCovid`  
**Nombre de Tabla**: `vacunas_covid`  
**Descripción**: Registro de vacunas COVID-19 aplicadas

#### Campos:

| Campo | Tipo | Requerido | Único | Indexado | Descripción |
|-------|------|-----------|-------|----------|-------------|
| `paciente_id` | uuid | ✅ | ❌ | ✅ | ID del paciente (relación con tabla pacientes) |
| `nombre_vacuna` | string | ✅ | ❌ | ❌ | Nombre comercial (Pfizer, Moderna, etc.) |
| `fabricante` | string | ✅ | ❌ | ❌ | Laboratorio fabricante |
| `lote` | string | ✅ | ✅ | ✅ | Número de lote (único) |
| `dosis_numero` | integer | ✅ | ❌ | ❌ | Número de dosis (1, 2, 3, refuerzo) |
| `fecha_aplicacion` | datetime | ✅ | ❌ | ✅ | Fecha y hora de aplicación |
| `lugar_aplicacion` | string | ✅ | ❌ | ❌ | Brazo izquierdo/derecho, muslo, etc. |
| `profesional_id` | uuid | ✅ | ❌ | ✅ | ID del profesional que aplicó (relación con usuarios) |
| `centro_vacunacion` | string | ❌ | ❌ | ❌ | Nombre del centro de vacunación |
| `efectos_adversos` | text | ❌ | ❌ | ❌ | Descripción de efectos adversos si los hubo |
| `certificado_emitido` | boolean | ✅ | ❌ | ❌ | Si se emitió certificado de vacunación |
| `proxima_dosis_fecha` | date | ❌ | ❌ | ❌ | Fecha programada para próxima dosis |

### Endpoints Generados:
- `POST /api/generated/vacunas_covid` - Registrar nueva vacuna
- `GET /api/generated/vacunas_covid` - Listar todas las vacunas
- `GET /api/generated/vacunas_covid/{id}` - Obtener vacuna por ID
- `GET /api/generated/vacunas_covid?paciente_id={uuid}` - Vacunas de un paciente
- `PUT /api/generated/vacunas_covid/{id}` - Actualizar registro
- `DELETE /api/generated/vacunas_covid/{id}` - Eliminar registro

---

## 2. 🌡️ Módulo de Alergias del Paciente

### Información del Módulo
- **ID**: `alergias-paciente`
- **Nombre**: Alergias del Paciente
- **Descripción**: Registro de alergias y reacciones adversas de pacientes
- **Categoría**: clinical
- **Color**: #ef4444 (rojo)

### Modelo: Alergia

**Nombre del Modelo**: `AlergiaPaciente`  
**Nombre de Tabla**: `alergias_pacientes`  
**Descripción**: Alergias y reacciones adversas registradas

#### Campos:

| Campo | Tipo | Requerido | Único | Indexado | Descripción |
|-------|------|-----------|-------|----------|-------------|
| `paciente_id` | uuid | ✅ | ❌ | ✅ | ID del paciente |
| `tipo_alergia` | string | ✅ | ❌ | ✅ | Medicamento, alimento, ambiental, etc. |
| `alergeno` | string | ✅ | ❌ | ✅ | Nombre del alérgeno (penicilina, maní, polen) |
| `severidad` | string | ✅ | ❌ | ✅ | leve, moderada, severa, anafilaxia |
| `sintomas` | text | ✅ | ❌ | ❌ | Descripción de síntomas |
| `fecha_primera_reaccion` | date | ✅ | ❌ | ❌ | Fecha de primera reacción conocida |
| `fecha_ultima_reaccion` | date | ❌ | ❌ | ❌ | Fecha de última reacción |
| `tratamiento_requerido` | text | ❌ | ❌ | ❌ | Tratamiento necesario en caso de exposición |
| `confirmada_por_medico` | boolean | ✅ | ❌ | ❌ | Si fue confirmada por profesional |
| `medico_confirma_id` | uuid | ❌ | ❌ | ❌ | ID del médico que confirmó |
| `notas_adicionales` | text | ❌ | ❌ | ❌ | Notas adicionales |
| `activa` | boolean | ✅ | ❌ | ✅ | Si la alergia sigue activa |

### Uso Clínico:
- Alertas automáticas al prescribir medicamentos
- Historial completo de alergias del paciente
- Filtrado por severidad para priorizar

---

## 3. 💊 Módulo de Medicamentos Recetados

### Información del Módulo
- **ID**: `medicamentos-recetados`
- **Nombre**: Medicamentos Recetados
- **Descripción**: Registro de medicamentos recetados a pacientes con seguimiento
- **Categoría**: clinical
- **Color**: #3b82f6 (azul)

### Modelo: Receta

**Nombre del Modelo**: `MedicamentoRecetado`  
**Nombre de Tabla**: `medicamentos_recetados`  
**Descripción**: Medicamentos recetados con seguimiento

#### Campos:

| Campo | Tipo | Requerido | Único | Indexado | Descripción |
|-------|------|-----------|-------|----------|-------------|
| `paciente_id` | uuid | ✅ | ❌ | ✅ | ID del paciente |
| `consulta_id` | uuid | ❌ | ❌ | ✅ | ID de la consulta donde se recetó |
| `medico_id` | uuid | ✅ | ❌ | ✅ | ID del médico que receta |
| `nombre_medicamento` | string | ✅ | ❌ | ✅ | Nombre comercial o genérico |
| `principio_activo` | string | ✅ | ❌ | ✅ | Componente activo |
| `dosis` | string | ✅ | ❌ | ❌ | Ej: "500mg", "10ml" |
| `frecuencia` | string | ✅ | ❌ | ❌ | Ej: "cada 8 horas", "2 veces al día" |
| `via_administracion` | string | ✅ | ❌ | ❌ | oral, intravenosa, tópica, etc. |
| `duracion_tratamiento` | integer | ✅ | ❌ | ❌ | Días de tratamiento |
| `fecha_inicio` | date | ✅ | ❌ | ✅ | Fecha de inicio del tratamiento |
| `fecha_fin` | date | ✅ | ❌ | ✅ | Fecha estimada de fin |
| `indicaciones` | text | ✅ | ❌ | ❌ | Instrucciones de uso |
| `efectos_secundarios` | text | ❌ | ❌ | ❌ | Efectos secundarios a vigilar |
| `contraindicaciones` | text | ❌ | ❌ | ❌ | Contraindicaciones |
| `cantidad_recetada` | integer | ✅ | ❌ | ❌ | Cantidad de unidades/cajas |
| `renovable` | boolean | ✅ | ❌ | ❌ | Si la receta es renovable |
| `estado` | string | ✅ | ❌ | ✅ | activa, completada, suspendida, cancelada |

---

## 4. 🩺 Módulo de Signos Vitales Extendidos

### Información del Módulo
- **ID**: `signos-vitales-ext`
- **Nombre**: Signos Vitales Extendidos
- **Descripción**: Registro detallado de signos vitales con seguimiento temporal
- **Categoría**: clinical
- **Color**: #8b5cf6 (morado)

### Modelo: SignoVital

**Nombre del Modelo**: `SignoVitalExtendido`  
**Nombre de Tabla**: `signos_vitales_extendidos`  
**Descripción**: Registro detallado de signos vitales

#### Campos:

| Campo | Tipo | Requerido | Único | Indexado | Descripción |
|-------|------|-----------|-------|----------|-------------|
| `paciente_id` | uuid | ✅ | ❌ | ✅ | ID del paciente |
| `consulta_id` | uuid | ❌ | ❌ | ✅ | ID de consulta asociada |
| `fecha_medicion` | datetime | ✅ | ❌ | ✅ | Fecha y hora de medición |
| `temperatura` | float | ❌ | ❌ | ❌ | Temperatura en °C |
| `presion_sistolica` | integer | ❌ | ❌ | ❌ | Presión sistólica (mmHg) |
| `presion_diastolica` | integer | ❌ | ❌ | ❌ | Presión diastólica (mmHg) |
| `frecuencia_cardiaca` | integer | ❌ | ❌ | ❌ | Latidos por minuto |
| `frecuencia_respiratoria` | integer | ❌ | ❌ | ❌ | Respiraciones por minuto |
| `saturacion_oxigeno` | float | ❌ | ❌ | ❌ | SpO2 en porcentaje |
| `peso` | float | ❌ | ❌ | ❌ | Peso en kg |
| `talla` | float | ❌ | ❌ | ❌ | Altura en cm |
| `imc` | float | ❌ | ❌ | ❌ | Índice de masa corporal |
| `glucosa` | float | ❌ | ❌ | ❌ | Glucosa en mg/dL |
| `medido_por_id` | uuid | ✅ | ❌ | ❌ | ID del profesional que midió |
| `observaciones` | text | ❌ | ❌ | ❌ | Observaciones adicionales |

---

## 5. 📅 Módulo de Citas de Seguimiento

### Información del Módulo
- **ID**: `citas-seguimiento`
- **Nombre**: Citas de Seguimiento
- **Descripción**: Programación y seguimiento de citas médicas
- **Categoría**: administrative
- **Color**: #f59e0b (naranja)

### Modelo: CitaSeguimiento

**Nombre del Modelo**: `CitaSeguimiento`  
**Nombre de Tabla**: `citas_seguimiento`  
**Descripción**: Citas programadas para seguimiento

#### Campos:

| Campo | Tipo | Requerido | Único | Indexado | Descripción |
|-------|------|-----------|-------|----------|-------------|
| `paciente_id` | uuid | ✅ | ❌ | ✅ | ID del paciente |
| `medico_id` | uuid | ✅ | ❌ | ✅ | ID del médico |
| `consulta_origen_id` | uuid | ❌ | ❌ | ✅ | Consulta que generó el seguimiento |
| `fecha_programada` | datetime | ✅ | ❌ | ✅ | Fecha y hora programada |
| `duracion_estimada` | integer | ✅ | ❌ | ❌ | Duración en minutos |
| `tipo_cita` | string | ✅ | ❌ | ✅ | control, seguimiento, urgencia, etc. |
| `motivo` | text | ✅ | ❌ | ❌ | Motivo de la cita |
| `estado` | string | ✅ | ❌ | ✅ | programada, confirmada, realizada, cancelada |
| `modalidad` | string | ✅ | ❌ | ❌ | presencial, telemedicina |
| `recordatorio_enviado` | boolean | ✅ | ❌ | ❌ | Si se envió recordatorio |
| `fecha_confirmacion` | datetime | ❌ | ❌ | ❌ | Cuándo confirmó el paciente |
| `notas_preparacion` | text | ❌ | ❌ | ❌ | Indicaciones previas (ayuno, etc.) |
| `sala_consultorio` | string | ❌ | ❌ | ❌ | Ubicación física |

---

## 6. 🔬 Módulo de Resultados de Laboratorio

### Información del Módulo
- **ID**: `resultados-lab`
- **Nombre**: Resultados de Laboratorio
- **Descripción**: Registro de resultados de exámenes de laboratorio
- **Categoría**: laboratory
- **Color**: #06b6d4 (cyan)

### Modelo: ResultadoLab

**Nombre del Modelo**: `ResultadoLaboratorio`  
**Nombre de Tabla**: `resultados_laboratorio`  
**Descripción**: Resultados de exámenes de laboratorio

#### Campos:

| Campo | Tipo | Requerido | Único | Indexado | Descripción |
|-------|------|-----------|-------|----------|-------------|
| `paciente_id` | uuid | ✅ | ❌ | ✅ | ID del paciente |
| `orden_id` | uuid | ❌ | ❌ | ✅ | ID de la orden de laboratorio |
| `medico_solicitante_id` | uuid | ✅ | ❌ | ✅ | Médico que solicitó |
| `tipo_examen` | string | ✅ | ❌ | ✅ | Tipo de examen (hemograma, glucosa, etc.) |
| `fecha_toma_muestra` | datetime | ✅ | ❌ | ✅ | Fecha de toma de muestra |
| `fecha_resultado` | datetime | ✅ | ❌ | ✅ | Fecha del resultado |
| `parametro` | string | ✅ | ❌ | ✅ | Parámetro medido |
| `valor` | string | ✅ | ❌ | ❌ | Valor obtenido |
| `unidad` | string | ✅ | ❌ | ❌ | Unidad de medida |
| `valor_referencia_min` | string | ❌ | ❌ | ❌ | Valor mínimo normal |
| `valor_referencia_max` | string | ❌ | ❌ | ❌ | Valor máximo normal |
| `estado` | string | ✅ | ❌ | ✅ | normal, alto, bajo, crítico |
| `observaciones` | text | ❌ | ❌ | ❌ | Observaciones del laboratorio |
| `laboratorio` | string | ✅ | ❌ | ❌ | Nombre del laboratorio |
| `revisado_por_medico` | boolean | ✅ | ❌ | ✅ | Si fue revisado por el médico |

---

## 🚀 Cómo Usar Estos Ejemplos

### Opción 1: Crear Manualmente en la Interfaz

1. Ve a **DDX Studio**
2. Click en **"Nuevo Módulo"**
3. Copia la información del módulo (ID, nombre, descripción, etc.)
4. Agrega el modelo con todos los campos según la tabla
5. Click en **"Crear Módulo"**
6. Click en **"Desplegar"** (botón verde ▶️)

### Opción 2: Importar via API (próximamente)

```bash
# Ejemplo de importación via API
curl -X POST http://localhost:8612/studio/modules/import \
  -H "Content-Type: application/json" \
  -d @vacunacion-covid.json
```

---

## 📊 Casos de Uso

### Vacunación COVID-19
- Registro de esquema completo de vacunación
- Seguimiento de efectos adversos
- Emisión de certificados
- Alertas de próximas dosis

### Alergias
- Alertas al prescribir medicamentos
- Historial completo del paciente
- Prevención de reacciones adversas

### Medicamentos Recetados
- Seguimiento de adherencia al tratamiento
- Detección de interacciones medicamentosas
- Renovación automática de recetas

### Signos Vitales
- Gráficas de evolución temporal
- Alertas de valores anormales
- Seguimiento de pacientes crónicos

### Citas de Seguimiento
- Recordatorios automáticos
- Gestión de agenda médica
- Seguimiento de tratamientos

### Resultados de Laboratorio
- Comparación con valores previos
- Alertas de valores críticos
- Integración con órdenes médicas

---

## 🔗 Relaciones con Sistema DDX

Todos estos módulos se relacionan con:
- **Pacientes** (`paciente_id` → tabla `pacientes`)
- **Usuarios/Médicos** (`medico_id`, `profesional_id` → tabla `usuarios`)
- **Consultas** (`consulta_id` → tabla `consultas`)

Esto permite:
- ✅ Ver toda la información del paciente en un solo lugar
- ✅ Trazabilidad completa de quién registró qué
- ✅ Contexto de cada registro (en qué consulta se generó)
- ✅ Reportes y estadísticas integradas

---

## 💡 Tips para Crear Tus Propios Módulos

1. **Siempre incluye `paciente_id`** para relacionar con pacientes
2. **Agrega campos de auditoría** como `medico_id`, `fecha_registro`
3. **Usa índices** en campos que usarás para búsquedas frecuentes
4. **Campos únicos** solo para identificadores realmente únicos (lotes, códigos)
5. **Campos de texto** para descripciones largas, `string` para cortos
6. **Campos booleanos** para estados binarios (activo/inactivo, confirmado/no)
7. **Campos de fecha** para seguimiento temporal

---

## 📞 Soporte

Si necesitas ayuda creando módulos personalizados, consulta:
- `DDX_STUDIO_README.md` - Documentación completa
- `/docs` - API documentation
- Logs del servidor para errores de despliegue
