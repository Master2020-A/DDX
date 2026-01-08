# 🎤 Integración de Captura por Voz en Consultas

## 📋 Guía de Integración

### **OPCIÓN 1: Integrar en NuevaConsulta.tsx (Recomendado)**

```tsx
import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import api from '@/lib/api'
import { Paciente } from '@/types'
import TranscripcionConsultaVoz from '@/components/TranscripcionConsultaVoz'

const NuevaConsulta = () => {
  const { pacienteId } = useParams()
  const navigate = useNavigate()
  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    tipo_consulta: 'primera_vez',
    motivo_consulta: '',
    sintomas: '',
    presion_arterial: '',
    frecuencia_cardiaca: '',
    temperatura: '',
    peso: '',
    talla: '',
  })
  const [error, setError] = useState('')

  useEffect(() => {
    if (pacienteId) {
      fetchPaciente(pacienteId)
    }
  }, [pacienteId])

  const fetchPaciente = async (id: string) => {
    try {
      const response = await api.get(`/pacientes/${id}`)
      setPaciente(response.data)
    } catch (error) {
      console.error('Error fetching paciente:', error)
    }
  }

  // 🎤 NUEVA FUNCIÓN: Manejar datos extraídos de la transcripción
  const handleDatosExtraidos = (datos: any) => {
    console.log('Datos extraídos:', datos)

    // Pre-llenar síntomas
    if (datos.sintomas && datos.sintomas.length > 0) {
      const sintomasTexto = datos.sintomas
        .map((s: any) => s.nombre || s)
        .join(', ')
      setFormData(prev => ({
        ...prev,
        sintomas: sintomasTexto,
      }))
    }

    // Pre-llenar signos vitales
    if (datos.signos_vitales) {
      const sv = datos.signos_vitales
      setFormData(prev => ({
        ...prev,
        presion_arterial: sv.presion_arterial || prev.presion_arterial,
        frecuencia_cardiaca: sv.frecuencia_cardiaca || prev.frecuencia_cardiaca,
        temperatura: sv.temperatura || prev.temperatura,
        peso: sv.peso || prev.peso,
        talla: sv.talla || prev.talla,
      }))
    }

    // Mostrar notificación de éxito
    alert('✅ Formulario pre-llenado con datos de la transcripción')
  }

  // 🎤 NUEVA FUNCIÓN: Manejar transcripción completa
  const handleTranscripcionCompleta = (texto: string) => {
    console.log('Transcripción completa:', texto)
    
    // Opcionalmente, usar el texto completo como motivo de consulta
    if (!formData.motivo_consulta) {
      setFormData(prev => ({
        ...prev,
        motivo_consulta: texto.substring(0, 500), // Limitar a 500 caracteres
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const data = {
        paciente_id: pacienteId,
        tipo_consulta: formData.tipo_consulta,
        motivo_consulta: formData.motivo_consulta,
        sintomas: formData.sintomas.split(',').map(s => s.trim()).filter(s => s),
        presion_arterial: formData.presion_arterial,
        frecuencia_cardiaca: formData.frecuencia_cardiaca,
        temperatura: formData.temperatura,
        peso: formData.peso,
        talla: formData.talla,
      }

      const response = await api.post('/consultas/', data)
      navigate(`/consultas/${response.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear consulta')
    } finally {
      setLoading(false)
    }
  }

  if (!paciente) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Cargando...</p>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <Link to={`/pacientes/${pacienteId}`} className="inline-flex items-center text-primary-600 hover:text-primary-700">
          <ArrowLeft size={20} className="mr-2" />
          Volver al paciente
        </Link>
      </div>

      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Nueva Consulta</h1>
        <p className="text-gray-600 mb-6">
          Paciente: <span className="font-medium">{paciente.nombre_completo}</span> ({paciente.numero_expediente})
        </p>

        {/* 🎤 COMPONENTE DE TRANSCRIPCIÓN POR VOZ */}
        <div className="mb-6">
          <TranscripcionConsultaVoz
            pacienteId={pacienteId!}
            onDatosExtraidos={handleDatosExtraidos}
            onTranscripcionCompleta={handleTranscripcionCompleta}
          />
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Consulta
            </label>
            <select
              value={formData.tipo_consulta}
              onChange={(e) => setFormData({ ...formData, tipo_consulta: e.target.value })}
              className="input"
            >
              <option value="primera_vez">Primera Vez</option>
              <option value="subsecuente">Subsecuente</option>
              <option value="urgencia">Urgencia</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Motivo de Consulta
            </label>
            <textarea
              value={formData.motivo_consulta}
              onChange={(e) => setFormData({ ...formData, motivo_consulta: e.target.value })}
              className="input"
              rows={3}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Síntomas (separados por comas)
            </label>
            <textarea
              value={formData.sintomas}
              onChange={(e) => setFormData({ ...formData, sintomas: e.target.value })}
              className="input"
              rows={3}
              placeholder="Ej: Fiebre, dolor de cabeza, tos"
            />
          </div>

          {/* Signos Vitales */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Presión Arterial
              </label>
              <input
                type="text"
                value={formData.presion_arterial}
                onChange={(e) => setFormData({ ...formData, presion_arterial: e.target.value })}
                className="input"
                placeholder="120/80"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Frecuencia Cardíaca
              </label>
              <input
                type="text"
                value={formData.frecuencia_cardiaca}
                onChange={(e) => setFormData({ ...formData, frecuencia_cardiaca: e.target.value })}
                className="input"
                placeholder="72 lpm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperatura (°C)
              </label>
              <input
                type="text"
                value={formData.temperatura}
                onChange={(e) => setFormData({ ...formData, temperatura: e.target.value })}
                className="input"
                placeholder="36.5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Peso (kg)
              </label>
              <input
                type="text"
                value={formData.peso}
                onChange={(e) => setFormData({ ...formData, peso: e.target.value })}
                className="input"
                placeholder="70"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1"
            >
              {loading ? 'Creando...' : 'Crear Consulta'}
            </button>
            <Link to={`/pacientes/${pacienteId}`} className="btn-secondary">
              Cancelar
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

export default NuevaConsulta
```

---

## 🎯 **OPCIÓN 2: Integrar en ConsultaDetalle.tsx (Para editar consultas existentes)**

```tsx
import TranscripcionConsultaVoz from '@/components/TranscripcionConsultaVoz'

// En el componente ConsultaDetalle
const [mostrarTranscripcion, setMostrarTranscripcion] = useState(false)

// Agregar botón
<button
  onClick={() => setMostrarTranscripcion(!mostrarTranscripcion)}
  className="btn-secondary flex items-center gap-2"
>
  <Mic className="w-4 h-4" />
  Agregar Nota por Voz
</button>

// Mostrar componente condicionalmente
{mostrarTranscripcion && (
  <div className="mt-4">
    <TranscripcionConsultaVoz
      pacienteId={consulta.paciente_id}
      onDatosExtraidos={(datos) => {
        // Agregar a notas de evolución
        console.log('Datos extraídos:', datos)
      }}
      onTranscripcionCompleta={(texto) => {
        // Agregar como nota
        agregarNota(texto)
      }}
    />
  </div>
)}
```

---

## 🚀 **FLUJO DE USO**

### **Escenario: Médico atendiendo paciente**

1. **Médico abre "Nueva Consulta"**
   - Ve el formulario tradicional
   - Ve el componente de "Captura de Consulta por Voz" arriba

2. **Médico hace clic en "Iniciar Grabación"**
   - El navegador pide permiso para usar el micrófono
   - Comienza a grabar (muestra cronómetro)

3. **Médico habla durante la consulta:**
   ```
   "Paciente masculino de 45 años que acude por dolor de cabeza
   de 3 días de evolución. Refiere que el dolor es pulsátil,
   localizado en región frontal, intensidad 7 de 10.
   
   Signos vitales: presión arterial 140 sobre 90,
   frecuencia cardíaca 85 latidos por minuto,
   temperatura 36.8 grados.
   
   Antecedente de hipertensión arterial en tratamiento con
   losartán 50 miligramos al día."
   ```

4. **Médico hace clic en "Detener Grabación"**
   - El audio se guarda localmente

5. **Médico hace clic en "Transcribir y Extraer Datos"**
   - El sistema envía el audio al backend
   - Whisper transcribe el audio
   - GPT-4o extrae información estructurada

6. **Sistema muestra resultados en modal:**
   - ✅ Texto transcrito completo
   - ✅ Síntomas extraídos: "Dolor de cabeza"
   - ✅ Signos vitales: PA 140/90, FC 85, Temp 36.8
   - ✅ Antecedentes: "Hipertensión arterial"
   - ✅ Medicamentos: "Losartán 50mg"

7. **Médico hace clic en "Aceptar y Continuar"**
   - El formulario se pre-llena automáticamente
   - Médico solo revisa y ajusta si es necesario
   - Guarda la consulta

---

## 📊 **DATOS QUE SE EXTRAEN AUTOMÁTICAMENTE**

### **Información Clínica:**
- ✅ Síntomas y su descripción
- ✅ Signos vitales (PA, FC, Temp, Peso, Talla, etc.)
- ✅ Diagnósticos mencionados
- ✅ Medicamentos actuales
- ✅ Antecedentes personales
- ✅ Alergias mencionadas
- ✅ Estudios solicitados

### **Formato de Extracción:**
```json
{
  "sintomas": [
    {
      "nombre": "Dolor de cabeza",
      "duracion": "3 días",
      "intensidad": "7/10",
      "caracteristicas": "pulsátil, frontal"
    }
  ],
  "signos_vitales": {
    "presion_arterial": "140/90",
    "frecuencia_cardiaca": "85",
    "temperatura": "36.8"
  },
  "medicamentos": [
    {
      "nombre": "Losartán",
      "dosis": "50mg",
      "frecuencia": "al día"
    }
  ],
  "antecedentes": [
    "Hipertensión arterial"
  ]
}
```

---

## ⚡ **VENTAJAS**

1. **⏱️ Ahorro de Tiempo:**
   - Médico habla naturalmente durante la consulta
   - No necesita escribir mientras atiende
   - Formulario se llena automáticamente

2. **✅ Mayor Precisión:**
   - No hay errores de transcripción manual
   - IA extrae datos estructurados
   - Médico solo revisa y confirma

3. **👨‍⚕️ Mejor Atención:**
   - Médico se concentra en el paciente
   - No pierde tiempo escribiendo
   - Interacción más humana

4. **📝 Documentación Completa:**
   - Texto completo de la consulta guardado
   - Datos estructurados para análisis
   - Historial clínico más detallado

5. **🔒 Seguridad:**
   - Audio procesado y eliminado
   - Solo se guarda la transcripción
   - Cumple con normativas médicas

---

## 🛠️ **PERSONALIZACIÓN**

### **Cambiar idioma de transcripción:**
```tsx
<TranscripcionConsultaVoz
  pacienteId={pacienteId}
  idioma="en" // Inglés
  onDatosExtraidos={handleDatosExtraidos}
/>
```

### **Deshabilitar extracción automática:**
```tsx
<TranscripcionConsultaVoz
  pacienteId={pacienteId}
  extraerInformacion={false} // Solo transcribir
  onTranscripcionCompleta={handleTranscripcion}
/>
```

### **Agregar validación personalizada:**
```tsx
const handleDatosExtraidos = (datos: any) => {
  // Validar datos antes de aplicar
  if (datos.signos_vitales?.presion_arterial) {
    const [sistolica, diastolica] = datos.signos_vitales.presion_arterial.split('/')
    if (parseInt(sistolica) > 180) {
      alert('⚠️ Presión arterial crítica detectada')
    }
  }
  
  // Aplicar datos
  setFormData(prev => ({ ...prev, ...datos }))
}
```

---

## 📱 **COMPATIBILIDAD**

- ✅ Chrome/Edge (Recomendado)
- ✅ Firefox
- ✅ Safari (iOS 14.5+)
- ✅ Dispositivos móviles
- ⚠️ Requiere HTTPS en producción
- ⚠️ Requiere permiso de micrófono

---

## 🔧 **SOLUCIÓN DE PROBLEMAS**

### **Error: "No se pudo acceder al micrófono"**
- Verificar permisos del navegador
- Usar HTTPS (no HTTP)
- Revisar configuración de privacidad

### **Error: "Error al transcribir el audio"**
- Verificar que el backend esté corriendo
- Verificar que OPENAI_API_KEY esté configurada
- Revisar logs del backend

### **Audio muy largo:**
- Detener y procesar en segmentos
- Whisper soporta hasta 25MB
- Considerar comprimir audio

---

## 📚 **PRÓXIMOS PASOS**

1. ✅ Integrar en `NuevaConsulta.tsx`
2. ✅ Probar con consultas reales
3. ⏳ Agregar soporte para múltiples idiomas
4. ⏳ Implementar grabación continua en segundo plano
5. ⏳ Agregar resumen automático al finalizar consulta

---

## 🎉 **¡LISTO PARA USAR!**

El componente está completamente funcional y listo para integrarse en cualquier formulario de consulta.
