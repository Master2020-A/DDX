# 🔬 Sistema de Laboratorio Clínico - Frontend

Interfaz completa para gestión de resultados de laboratorio con análisis automatizado, visualización de tendencias y alertas inteligentes.

---

## 📦 **COMPONENTES IMPLEMENTADOS**

### **1. FormularioLaboratorio.tsx**
Formulario inteligente para captura de resultados.

**Características:**
- ✅ Selección dinámica de área y tipo de prueba
- ✅ Campos auto-generados según tipo de prueba
- ✅ Validación con rangos de referencia en tiempo real
- ✅ Tooltips informativos por parámetro
- ✅ Soporte para parámetros personalizados
- ✅ Análisis automático al guardar

**Props:**
```typescript
interface FormularioLaboratorioProps {
  pacienteId: string;
  consultaId?: string;
  onSuccess?: (prueba: any) => void;
  onCancel?: () => void;
}
```

---

### **2. DashboardLaboratorio.tsx**
Dashboard principal con estadísticas y listado de pruebas.

**Características:**
- ✅ 4 tarjetas de estadísticas (Total, Normales, Atención, Críticos)
- ✅ Listado con filtros por área
- ✅ Indicadores visuales de estado (colores, iconos)
- ✅ 3 pestañas: Historial, Detalle, Tendencias
- ✅ Navegación fluida entre vistas

**Props:**
```typescript
interface DashboardLaboratorioProps {
  pacienteId: string;
}
```

---

### **3. DetallePruebaLaboratorio.tsx**
Vista detallada de resultados con interpretación clínica.

**Características:**
- ✅ Alertas destacadas para valores críticos
- ✅ Tabla completa de resultados con rangos
- ✅ Indicadores de estado por parámetro
- ✅ Interpretación clínica formateada
- ✅ Notas del médico
- ✅ Código de colores (verde/amarillo/rojo)

**Props:**
```typescript
interface DetallePruebaLaboratorioProps {
  pruebaId: string;
  onClose?: () => void;
}
```

---

### **4. GraficaTendencias.tsx**
Gráficas interactivas de evolución temporal.

**Características:**
- ✅ Gráfica de líneas con Recharts
- ✅ Selección de parámetro a visualizar
- ✅ Líneas de referencia (min/max)
- ✅ Puntos coloreados según estado
- ✅ Tooltip informativo
- ✅ Leyenda de colores

**Props:**
```typescript
interface GraficaTendenciasProps {
  pacienteId: string;
  pruebas: PruebaLaboratorioResumen[];
}
```

---

### **5. Laboratorios.tsx (Página)**
Página principal que integra todos los componentes.

**Ruta:**
```
/laboratorios/:pacienteId
```

---

## 🎨 **TIPOS Y CONSTANTES**

### **Áreas Disponibles:**
```typescript
- hematologia: Hematología
- quimica_clinica: Química Clínica
- bacteriologia: Bacteriología
- inmunologia: Inmunología
- parasitologia: Parasitología
- urinalisis: Examen General de Orina
```

### **Tipos de Pruebas:**

**Hematología:**
- Biometría Hemática Completa (10 parámetros)
- VSG

**Química Clínica:**
- Glucosa en Ayunas
- Función Renal (3 parámetros)
- Perfil Lipídico (4 parámetros)
- Función Hepática (6 parámetros)

**Inmunología:**
- Marcadores Inflamatorios (PCR)

---

## 🚀 **USO**

### **1. Acceder a Laboratorios**

Desde el detalle de un paciente:
```typescript
navigate(`/laboratorios/${pacienteId}`);
```

### **2. Registrar Nuevo Resultado**

1. Click en **"Nuevo Resultado"**
2. Seleccionar **Área** (ej: Hematología)
3. Seleccionar **Tipo de Prueba** (ej: Biometría Hemática)
4. Los campos se generan automáticamente
5. Ingresar valores
6. Click **"Guardar y Analizar"**

El sistema automáticamente:
- ✅ Compara con rangos de referencia
- ✅ Detecta valores anormales
- ✅ Identifica valores críticos
- ✅ Genera interpretación clínica
- ✅ Marca si requiere atención

### **3. Ver Detalle de Prueba**

1. En el historial, click en el ícono 👁️
2. Se muestra:
   - Alertas de valores críticos (rojo)
   - Alertas de valores anormales (amarillo)
   - Tabla completa de resultados
   - Interpretación clínica
   - Notas del médico

### **4. Ver Tendencias**

1. Click en pestaña **"Tendencias"**
2. Seleccionar parámetro (ej: Glucosa)
3. Se muestra gráfica con:
   - Evolución temporal
   - Líneas de referencia
   - Puntos coloreados por estado
   - Tooltip con detalles

---

## 🎯 **EJEMPLOS DE USO**

### **Ejemplo 1: Biometría Hemática Normal**

```typescript
// Datos ingresados
{
  area: 'hematologia',
  tipo_prueba: 'biometria_hematica',
  resultados: [
    { parametro: 'hemoglobina', valor: 14.5 },
    { parametro: 'leucocitos', valor: 7.5 },
    { parametro: 'plaquetas', valor: 250 }
  ]
}

// Resultado mostrado
✅ Todos los valores dentro de rangos normales
```

### **Ejemplo 2: Glucosa Alta**

```typescript
// Datos ingresados
{
  area: 'quimica_clinica',
  tipo_prueba: 'glucosa',
  resultados: [
    { parametro: 'glucosa', valor: 180 }
  ]
}

// Resultado mostrado
⚠️ Valores fuera de rango normal:
• ↑ glucosa alto (180.0 mg/dL, normal: 70.0-100.0)
  Hiperglucemia - descartar diabetes mellitus

💡 Interpretación clínica:
• Hiperglucemia - Descartar diabetes mellitus o prediabetes
```

### **Ejemplo 3: Valor Crítico**

```typescript
// Datos ingresados
{
  area: 'quimica_clinica',
  tipo_prueba: 'glucosa',
  resultados: [
    { parametro: 'glucosa', valor: 35 }
  ]
}

// Resultado mostrado
🚨 VALORES CRÍTICOS - ATENCIÓN INMEDIATA:
• ⚠️ CRÍTICO: glucosa muy bajo (35.0 mg/dL)
  Hipoglucemia - requiere atención inmediata

💡 Interpretación clínica:
• Hipoglucemia - Requiere evaluación urgente
```

---

## 📊 **VISUALIZACIÓN DE ESTADOS**

### **Colores:**
- 🟢 **Verde:** Valores normales
- 🟡 **Amarillo:** Valores anormales (fuera de rango)
- 🔴 **Rojo:** Valores críticos (atención inmediata)

### **Iconos:**
- ✅ **CheckCircle:** Normal
- ⚠️ **Warning:** Anormal
- 🚨 **Error:** Crítico
- ↓ **TrendingDown:** Bajo
- ↑ **TrendingUp:** Alto

---

## 🔧 **INTEGRACIÓN CON BACKEND**

### **Endpoints Utilizados:**

```typescript
// Crear prueba
POST /api/laboratorio/
Body: CrearPruebaLaboratorio

// Listar pruebas de paciente
GET /api/laboratorio/paciente/{pacienteId}?area=hematologia

// Obtener detalle
GET /api/laboratorio/{pruebaId}

// Obtener rangos
GET /api/laboratorio/rangos/area/{area}
```

---

## 📱 **RESPONSIVE DESIGN**

Todos los componentes son responsive:
- **Desktop:** Grid de 12 columnas
- **Tablet:** Grid adaptativo (6-8 columnas)
- **Mobile:** Stack vertical (12 columnas)

---

## 🎨 **PERSONALIZACIÓN**

### **Agregar Nuevo Parámetro:**

1. Editar `types/laboratorio.ts`:
```typescript
export const PARAMETROS_LABELS: Record<string, string> = {
  // ... existentes
  nuevo_parametro: 'Nuevo Parámetro'
};
```

2. Agregar a tipo de prueba:
```typescript
export const TIPOS_PRUEBAS = {
  quimica_clinica: [
    {
      value: 'nueva_prueba',
      label: 'Nueva Prueba',
      parametros: ['nuevo_parametro']
    }
  ]
};
```

3. Agregar rango en backend (ver `SISTEMA_LABORATORIO.md`)

---

## 🐛 **TROUBLESHOOTING**

### **Error: "No hay parámetros disponibles"**

**Causa:** No hay pruebas registradas o no tienen resultados.

**Solución:** Registra al menos una prueba con resultados.

### **Gráfica no muestra datos**

**Causa:** El parámetro seleccionado no existe en ninguna prueba.

**Solución:** Selecciona un parámetro que esté presente en las pruebas registradas.

### **Rangos no se muestran**

**Causa:** No se han cargado los rangos de referencia en el backend.

**Solución:** Ejecuta `python inicializar_rangos_laboratorio.py`

---

## 📈 **PRÓXIMAS MEJORAS**

- [ ] Exportar reportes en PDF
- [ ] Comparación con estudios previos
- [ ] Alertas por email/SMS para valores críticos
- [ ] Gráficas de múltiples parámetros
- [ ] Filtros avanzados (fecha, estado, área)
- [ ] Importación desde archivos CSV/Excel
- [ ] Integración con sistemas de laboratorio externos (HL7)

---

## 📞 **SOPORTE**

Para reportar bugs o solicitar nuevas funcionalidades, contacta al equipo de desarrollo.

---

**Versión:** 1.0.0  
**Última actualización:** Diciembre 2024
