# 🔬 Recurso Observation HL7 FHIR R4

## Documentación Completa del Sistema de Observaciones FHIR

**Versión:** 1.0.0  
**Estándar:** HL7 FHIR R4  
**Fecha:** Diciembre 2024

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Modelo de Datos](#modelo-de-datos)
4. [Endpoints API](#endpoints-api)
5. [Transformadores](#transformadores)
6. [Códigos LOINC](#códigos-loinc)
7. [Ejemplos de Uso](#ejemplos-de-uso)
8. [Integración](#integración)

---

## 🎯 Introducción

El recurso **Observation** es uno de los recursos centrales de HL7 FHIR. Representa mediciones y observaciones clínicas simples o complejas, incluyendo:

- **Signos vitales**: Presión arterial, temperatura, frecuencia cardíaca, etc.
- **Resultados de laboratorio**: Glucosa, hemoglobina, creatinina, etc.
- **Mediciones físicas**: Peso, talla, IMC
- **Observaciones clínicas**: Hallazgos de examen físico
- **Resultados de estudios**: EKG, EEG, imágenes

### Características Implementadas

✅ Soporte completo para FHIR R4  
✅ Códigos LOINC para estandarización  
✅ Observaciones simples y multi-componente  
✅ Rangos de referencia automáticos  
✅ Interpretación automática (Normal, High, Low, Critical)  
✅ Transformadores para datos existentes  
✅ Búsqueda con parámetros FHIR  
✅ Bundles para múltiples observaciones  
✅ Trazabilidad con datos originales  

---

## 🏗️ Arquitectura

### Componentes

```
┌─────────────────────────────────────────┐
│         API Endpoints                   │
│  /api/fhir/observations                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Transformadores                 │
│  - Signos Vitales → Observation         │
│  - Laboratorio → Observation            │
│  - Presión Arterial → Multi-componente  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Modelo FHIR Observation         │
│  - Validación Pydantic                  │
│  - Almacenamiento PostgreSQL            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Base de Datos                   │
│  - Tabla: fhir_observations             │
│  - Índices optimizados                  │
└─────────────────────────────────────────┘
```

### Flujo de Datos

1. **Captura**: Datos clínicos capturados en el sistema (consulta, laboratorio, etc.)
2. **Transformación**: Convertidos a formato FHIR con códigos LOINC
3. **Validación**: Validados con schemas Pydantic
4. **Almacenamiento**: Guardados en tabla `fhir_observations`
5. **Recuperación**: Consultados vía API REST con filtros FHIR
6. **Intercambio**: Exportados en Bundles FHIR para interoperabilidad

---

## 📊 Modelo de Datos

### Estructura de la Tabla

```sql
CREATE TABLE fhir_observations (
    -- Identificación
    id UUID PRIMARY KEY,
    identifier JSONB,
    
    -- Estado y categoría
    status observation_status NOT NULL,
    category TEXT[],
    
    -- Código (LOINC, SNOMED, etc)
    code JSONB NOT NULL,
    
    -- Referencias
    subject_type VARCHAR(50),
    subject_id UUID REFERENCES pacientes(id),
    encounter_id UUID REFERENCES consultas(id),
    
    -- Tiempo
    effective_datetime TIMESTAMP,
    effective_period_start TIMESTAMP,
    effective_period_end TIMESTAMP,
    issued TIMESTAMP,
    
    -- Performer
    performer JSONB,
    
    -- Valores (solo uno presente)
    value_quantity JSONB,
    value_codeable_concept JSONB,
    value_string TEXT,
    value_boolean BOOLEAN,
    value_integer INTEGER,
    value_range JSONB,
    value_ratio JSONB,
    value_time VARCHAR(20),
    value_datetime TIMESTAMP,
    value_period JSONB,
    
    -- Interpretación y notas
    interpretation JSONB,
    note JSONB,
    
    -- Método y sitio
    method JSONB,
    body_site JSONB,
    
    -- Rango de referencia
    reference_range JSONB,
    
    -- Componentes (multi-valor)
    component JSONB,
    
    -- Metadatos
    meta JSONB,
    source_type VARCHAR(50),
    source_id UUID,
    
    -- Auditoría
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by UUID
);
```

### Estados de Observación

| Estado | Descripción |
|--------|-------------|
| `registered` | Registrada pero no realizada |
| `preliminary` | Resultado preliminar |
| `final` | Resultado final |
| `amended` | Modificada después de final |
| `corrected` | Corregida |
| `cancelled` | Cancelada |
| `entered-in-error` | Ingresada por error |
| `unknown` | Estado desconocido |

### Categorías

| Categoría | Descripción |
|-----------|-------------|
| `vital-signs` | Signos vitales |
| `laboratory` | Laboratorio clínico |
| `imaging` | Estudios de imagen |
| `procedure` | Procedimientos |
| `survey` | Encuestas |
| `exam` | Examen físico |
| `therapy` | Terapia |
| `activity` | Actividad |

---

## 🔌 Endpoints API

### Base URL
```
/api/fhir/observations
```

### 1. Crear Observation

**POST** `/api/fhir/observations/`

```json
{
  "status": "final",
  "category": ["laboratory"],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "2345-7",
      "display": "Glucose"
    }],
    "text": "Glucosa"
  },
  "subject_id": "uuid-del-paciente",
  "effective_datetime": "2024-12-21T10:30:00Z",
  "value_quantity": {
    "value": 95,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  },
  "interpretation": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
      "code": "N",
      "display": "Normal"
    }]
  }],
  "reference_range": [{
    "low": {"value": 70, "unit": "mg/dL"},
    "high": {"value": 100, "unit": "mg/dL"}
  }]
}
```

### 2. Listar Observations

**GET** `/api/fhir/observations/`

**Parámetros de búsqueda:**
- `patient`: UUID del paciente
- `category`: Categoría (vital-signs, laboratory, etc)
- `code`: Código LOINC
- `date`: Fecha (YYYY-MM-DD)
- `status`: Estado
- `skip`: Offset para paginación
- `limit`: Límite de resultados

**Ejemplo:**
```
GET /api/fhir/observations/?patient=uuid&category=laboratory&skip=0&limit=50
```

### 3. Obtener Observation por ID

**GET** `/api/fhir/observations/{observation_id}`

### 4. Actualizar Observation

**PUT** `/api/fhir/observations/{observation_id}`

### 5. Eliminar Observation

**DELETE** `/api/fhir/observations/{observation_id}`

### 6. Obtener en Formato FHIR Completo

**GET** `/api/fhir/observations/{observation_id}/fhir`

Retorna el recurso en formato FHIR R4 estándar completo.

### 7. Obtener Bundle de Paciente

**GET** `/api/fhir/observations/patient/{patient_id}/bundle`

Retorna todas las observaciones del paciente en un Bundle FHIR.

### 8. Crear desde Signo Vital

**POST** `/api/fhir/observations/from-vital-sign`

```json
{
  "nombre_parametro": "frecuencia_cardiaca",
  "valor": 75,
  "unidad": "bpm",
  "paciente_id": "uuid",
  "consulta_id": "uuid",
  "fecha": "2024-12-21T10:30:00Z"
}
```

### 9. Crear desde Presión Arterial

**POST** `/api/fhir/observations/from-blood-pressure`

```json
{
  "sistolica": 120,
  "diastolica": 80,
  "paciente_id": "uuid",
  "consulta_id": "uuid",
  "fecha": "2024-12-21T10:30:00Z"
}
```

### 10. Crear desde Parámetro de Laboratorio

**POST** `/api/fhir/observations/from-lab-parameter`

```json
{
  "nombre_parametro": "hemoglobina",
  "valor": 14.5,
  "unidad": "g/dL",
  "paciente_id": "uuid",
  "prueba_id": "uuid",
  "fecha": "2024-12-21T10:30:00Z",
  "interpretacion": "Valor dentro de rangos normales",
  "estado_anormal": null
}
```

### 11. Estadísticas

**GET** `/api/fhir/observations/statistics/summary`

```json
{
  "total": 150,
  "por_categoria": {
    "vital-signs": 80,
    "laboratory": 70
  },
  "por_estado": {
    "final": 140,
    "preliminary": 10
  },
  "ultima_actualizacion": "2024-12-21T10:30:00Z"
}
```

---

## 🔄 Transformadores

### Transformador de Signos Vitales

```python
from app.services.fhir_observation_transformer import FHIRObservationTransformer

# Transformar signo vital
observation_data = FHIRObservationTransformer.from_signo_vital(
    nombre_parametro="frecuencia_cardiaca",
    valor=75,
    unidad="bpm",
    paciente_id=paciente_id,
    consulta_id=consulta_id,
    fecha=datetime.now(),
    medico_id=medico_id
)
```

**Características:**
- Mapeo automático a códigos LOINC
- Rangos de referencia automáticos
- Interpretación automática (Normal/High/Low)
- Unidades estandarizadas UCUM

### Transformador de Laboratorio

```python
observation_data = FHIRObservationTransformer.from_parametro_laboratorio(
    nombre_parametro="glucosa",
    valor=95,
    unidad="mg/dL",
    paciente_id=paciente_id,
    prueba_id=prueba_id,
    fecha=datetime.now(),
    medico_id=medico_id,
    interpretacion="Valor normal",
    estado_anormal=None
)
```

### Transformador de Presión Arterial (Multi-componente)

```python
observation_data = FHIRObservationTransformer.from_presion_arterial(
    sistolica=120,
    diastolica=80,
    paciente_id=paciente_id,
    consulta_id=consulta_id,
    fecha=datetime.now(),
    medico_id=medico_id
)
```

**Resultado:**
```json
{
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "85354-9",
      "display": "Blood pressure panel"
    }]
  },
  "component": [
    {
      "code": {"coding": [{"code": "8480-6", "display": "Systolic"}]},
      "valueQuantity": {"value": 120, "unit": "mmHg"}
    },
    {
      "code": {"coding": [{"code": "8462-4", "display": "Diastolic"}]},
      "valueQuantity": {"value": 80, "unit": "mmHg"}
    }
  ]
}
```

---

## 🏷️ Códigos LOINC

### Signos Vitales

| Parámetro | Código LOINC | Display |
|-----------|--------------|---------|
| Presión arterial sistólica | 8480-6 | Systolic blood pressure |
| Presión arterial diastólica | 8462-4 | Diastolic blood pressure |
| Frecuencia cardíaca | 8867-4 | Heart rate |
| Frecuencia respiratoria | 9279-1 | Respiratory rate |
| Temperatura | 8310-5 | Body temperature |
| Saturación de oxígeno | 2708-6 | Oxygen saturation |
| Peso | 29463-7 | Body weight |
| Talla | 8302-2 | Body height |
| IMC | 39156-5 | Body mass index |

### Hematología

| Parámetro | Código LOINC | Display |
|-----------|--------------|---------|
| Hemoglobina | 718-7 | Hemoglobin |
| Hematocrito | 4544-3 | Hematocrit |
| Leucocitos | 6690-2 | Leukocytes |
| Plaquetas | 777-3 | Platelets |
| Eritrocitos | 789-8 | Erythrocytes |

### Química Clínica

| Parámetro | Código LOINC | Display |
|-----------|--------------|---------|
| Glucosa | 2345-7 | Glucose |
| Creatinina | 2160-0 | Creatinine |
| Urea | 3094-0 | Urea nitrogen |
| Ácido úrico | 3084-1 | Uric acid |
| Colesterol total | 2093-3 | Cholesterol |
| Triglicéridos | 2571-8 | Triglyceride |
| HDL | 2085-9 | HDL Cholesterol |
| LDL | 2089-1 | LDL Cholesterol |
| TGO (AST) | 1920-8 | Aspartate aminotransferase |
| TGP (ALT) | 1742-6 | Alanine aminotransferase |
| Bilirrubina total | 1975-2 | Bilirubin.total |
| Fosfatasa alcalina | 6768-6 | Alkaline phosphatase |

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Crear Observación de Glucosa

```python
from app.schemas.fhir_observation import ObservationCreate, CodeableConcept, Coding, Quantity

observation = ObservationCreate(
    status="final",
    category=["laboratory"],
    code=CodeableConcept(
        coding=[Coding(
            system="http://loinc.org",
            code="2345-7",
            display="Glucose"
        )],
        text="Glucosa"
    ),
    subject_id=paciente_id,
    effective_datetime=datetime.now(),
    value_quantity=Quantity(
        value=95,
        unit="mg/dL",
        system="http://unitsofmeasure.org",
        code="mg/dL"
    )
)

# Crear en la base de datos
nueva_obs = FHIRObservation(**observation.model_dump())
db.add(nueva_obs)
await db.commit()
```

### Ejemplo 2: Buscar Observaciones de Laboratorio

```python
from sqlalchemy import select

# Buscar todas las observaciones de laboratorio de un paciente
query = select(FHIRObservation).where(
    and_(
        FHIRObservation.subject_id == paciente_id,
        FHIRObservation.category.contains(["laboratory"])
    )
).order_by(FHIRObservation.effective_datetime.desc())

result = await db.execute(query)
observations = result.scalars().all()
```

### Ejemplo 3: Crear Bundle FHIR

```python
from app.services.fhir_observation_transformer import FHIRObservationTransformer

# Obtener observaciones
observations = await db.execute(
    select(FHIRObservation).where(FHIRObservation.subject_id == paciente_id)
)
obs_list = observations.scalars().all()

# Crear bundle
bundle = FHIRObservationTransformer.crear_bundle_observations(obs_list)

# Resultado
{
    "resourceType": "Bundle",
    "type": "searchset",
    "total": 10,
    "entry": [
        {
            "fullUrl": "Observation/uuid-1",
            "resource": { ... }
        },
        ...
    ]
}
```

### Ejemplo 4: Integración con Consulta

```python
# Al guardar signos vitales en una consulta
async def guardar_signos_vitales(consulta_id, paciente_id, signos_vitales):
    # Crear observaciones FHIR para cada signo vital
    for nombre, valor in signos_vitales.items():
        obs_data = FHIRObservationTransformer.from_signo_vital(
            nombre_parametro=nombre,
            valor=valor['valor'],
            unidad=valor['unidad'],
            paciente_id=paciente_id,
            consulta_id=consulta_id,
            fecha=datetime.now()
        )
        
        observation = FHIRObservation(**obs_data)
        db.add(observation)
    
    await db.commit()
```

---

## 🔗 Integración

### Con Módulo de Laboratorio

```python
# En app/api/laboratorio.py
from app.services.fhir_observation_transformer import FHIRObservationTransformer
from app.models.fhir_observation import FHIRObservation

@router.post("/")
async def crear_prueba_laboratorio(prueba: PruebaLaboratorioCreate, db: AsyncSession):
    # Crear prueba de laboratorio
    nueva_prueba = PruebaLaboratorio(**prueba.model_dump())
    db.add(nueva_prueba)
    await db.commit()
    
    # Crear observaciones FHIR para cada parámetro
    for parametro in prueba.parametros:
        obs_data = FHIRObservationTransformer.from_parametro_laboratorio(
            nombre_parametro=parametro['nombre'],
            valor=parametro['valor'],
            unidad=parametro['unidad'],
            paciente_id=prueba.paciente_id,
            prueba_id=nueva_prueba.id,
            fecha=prueba.fecha_toma,
            interpretacion=parametro.get('interpretacion'),
            estado_anormal=parametro.get('estado')
        )
        
        observation = FHIRObservation(**obs_data, created_by=current_user.id)
        db.add(observation)
    
    await db.commit()
    return nueva_prueba
```

### Con Módulo de Consultas

```python
# En app/api/consultas.py
@router.post("/")
async def crear_consulta(consulta: ConsultaCreate, db: AsyncSession):
    # Crear consulta
    nueva_consulta = Consulta(**consulta.model_dump())
    db.add(nueva_consulta)
    await db.commit()
    
    # Crear observaciones FHIR para signos vitales
    if consulta.signos_vitales:
        # Presión arterial (multi-componente)
        if 'presion_arterial' in consulta.signos_vitales:
            pa = consulta.signos_vitales['presion_arterial']
            obs_data = FHIRObservationTransformer.from_presion_arterial(
                sistolica=pa['sistolica'],
                diastolica=pa['diastolica'],
                paciente_id=consulta.paciente_id,
                consulta_id=nueva_consulta.id,
                fecha=consulta.fecha_consulta
            )
            db.add(FHIRObservation(**obs_data))
        
        # Otros signos vitales
        for nombre, datos in consulta.signos_vitales.items():
            if nombre != 'presion_arterial':
                obs_data = FHIRObservationTransformer.from_signo_vital(
                    nombre_parametro=nombre,
                    valor=datos['valor'],
                    unidad=datos['unidad'],
                    paciente_id=consulta.paciente_id,
                    consulta_id=nueva_consulta.id,
                    fecha=consulta.fecha_consulta
                )
                db.add(FHIRObservation(**obs_data))
    
    await db.commit()
    return nueva_consulta
```

---

## 📝 Notas Importantes

### Validación

- Solo un tipo de valor puede estar presente por observación
- Las observaciones multi-componente usan el campo `component`
- El tiempo efectivo es obligatorio (datetime o period)
- El código es obligatorio y debe seguir CodeableConcept

### Rendimiento

- Índices GIN en campos JSONB para búsquedas rápidas
- Índice en `effective_datetime` para ordenamiento temporal
- Índice en `category` para filtrado por tipo
- Vista materializada `v_fhir_observations_summary` para consultas frecuentes

### Interoperabilidad

- Compatible con FHIR R4
- Códigos LOINC para estandarización internacional
- Unidades UCUM para mediciones
- Interpretaciones según CodeSystem v3-ObservationInterpretation

---

## 🚀 Próximos Pasos

1. **Frontend**: Componente React para visualizar observaciones FHIR
2. **Sincronización**: Sincronizar automáticamente al crear laboratorios/signos vitales
3. **Búsqueda avanzada**: Implementar más parámetros de búsqueda FHIR
4. **Validación FHIR**: Validar contra perfiles FHIR oficiales
5. **Export**: Exportar a formato FHIR JSON/XML
6. **Import**: Importar observaciones desde otros sistemas FHIR

---

**Documentación actualizada:** 21 de diciembre de 2024
