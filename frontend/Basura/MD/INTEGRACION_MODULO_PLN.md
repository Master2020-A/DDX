# 🎨 INTEGRACIÓN DEL MÓDULO PLN EN EL FRONTEND

## 📋 **COMPONENTE YA CREADO**

El componente `ModuloPLN.tsx` ya está disponible en:
```
frontend/src/components/ModuloPLN.tsx
```

---

## 🚀 **OPCIÓN 1: INTEGRAR EN PERFIL DE PACIENTE**

### **Paso 1: Importar el componente**

Edita `frontend/src/pages/PacienteDetalle.tsx`:

```tsx
import ModuloPLN from '@/components/ModuloPLN';
```

### **Paso 2: Agregar botón en la interfaz**

Agrega un botón junto a los demás botones de acción:

```tsx
// Dentro del componente PacienteDetalle, en la sección de botones

<Button
  variant="contained"
  startIcon={<Brain />}
  onClick={() => setMostrarPLN(true)}
  sx={{
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    '&:hover': {
      background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
    }
  }}
>
  🧠 Módulo PLN
</Button>
```

### **Paso 3: Agregar estado y diálogo**

```tsx
// Agregar estado
const [mostrarPLN, setMostrarPLN] = useState(false);

// Agregar diálogo al final del componente
<Dialog
  open={mostrarPLN}
  onClose={() => setMostrarPLN(false)}
  maxWidth="lg"
  fullWidth
>
  <DialogTitle>
    🧠 Procesamiento de Lenguaje Natural
    <IconButton
      onClick={() => setMostrarPLN(false)}
      sx={{ position: 'absolute', right: 8, top: 8 }}
    >
      <Close />
    </IconButton>
  </DialogTitle>
  <DialogContent>
    <ModuloPLN pacienteId={pacienteId} />
  </DialogContent>
</Dialog>
```

---

## 🚀 **OPCIÓN 2: CREAR PÁGINA DEDICADA**

### **Paso 1: Crear nueva página**

Crea `frontend/src/pages/ModuloPLNPage.tsx`:

```tsx
import React from 'react';
import { useParams } from 'react-router-dom';
import { Container, Paper, Typography, Box, Breadcrumbs, Link } from '@mui/material';
import { Home, Person, Brain } from '@mui/icons-material';
import ModuloPLN from '@/components/ModuloPLN';

export default function ModuloPLNPage() {
  const { pacienteId } = useParams<{ pacienteId: string }>();

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link href="/" color="inherit" sx={{ display: 'flex', alignItems: 'center' }}>
          <Home sx={{ mr: 0.5 }} fontSize="small" />
          Inicio
        </Link>
        <Link href="/pacientes" color="inherit" sx={{ display: 'flex', alignItems: 'center' }}>
          <Person sx={{ mr: 0.5 }} fontSize="small" />
          Pacientes
        </Link>
        <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
          <Brain sx={{ mr: 0.5 }} fontSize="small" />
          Módulo PLN
        </Typography>
      </Breadcrumbs>

      {/* Título */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          🧠 Procesamiento de Lenguaje Natural
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Herramientas de IA para transcripción, extracción, resúmenes y traducción médica
        </Typography>
      </Paper>

      {/* Componente PLN */}
      <ModuloPLN pacienteId={pacienteId!} />
    </Container>
  );
}
```

### **Paso 2: Agregar ruta**

Edita `frontend/src/App.tsx` o tu archivo de rutas:

```tsx
import ModuloPLNPage from './pages/ModuloPLNPage';

// Dentro de tus rutas
<Route path="/pacientes/:pacienteId/pln" element={<ModuloPLNPage />} />
```

### **Paso 3: Agregar enlace en menú de paciente**

En `PacienteDetalle.tsx`:

```tsx
<Button
  variant="outlined"
  startIcon={<Brain />}
  component={Link}
  to={`/pacientes/${pacienteId}/pln`}
>
  Módulo PLN
</Button>
```

---

## 🚀 **OPCIÓN 3: INTEGRAR EN CONSULTA**

### **Usar durante la consulta para transcribir audio**

En `FormularioConsulta.tsx`:

```tsx
import { useState } from 'react';
import { Dialog, DialogContent, DialogTitle, IconButton, Button } from '@mui/material';
import { Mic, Close } from '@mui/icons-material';
import ModuloPLN from '@/components/ModuloPLN';

// Dentro del componente
const [mostrarTranscripcion, setMostrarTranscripcion] = useState(false);

// Botón para abrir transcripción
<Button
  variant="outlined"
  startIcon={<Mic />}
  onClick={() => setMostrarTranscripcion(true)}
>
  Transcribir Audio
</Button>

// Diálogo con solo la pestaña de transcripción
<Dialog
  open={mostrarTranscripcion}
  onClose={() => setMostrarTranscripcion(false)}
  maxWidth="md"
  fullWidth
>
  <DialogTitle>
    🎤 Transcribir Consulta
    <IconButton
      onClick={() => setMostrarTranscripcion(false)}
      sx={{ position: 'absolute', right: 8, top: 8 }}
    >
      <Close />
    </IconButton>
  </DialogTitle>
  <DialogContent>
    <ModuloPLN pacienteId={pacienteId} />
  </DialogContent>
</Dialog>
```

---

## 🎯 **PERSONALIZACIÓN DEL COMPONENTE**

### **Mostrar solo una funcionalidad específica**

Modifica `ModuloPLN.tsx` para aceptar props:

```tsx
interface ModuloPLNProps {
  pacienteId: string;
  defaultTab?: 'transcripcion' | 'extraccion' | 'resumen' | 'traduccion';
  hideOtherTabs?: boolean;
}

export default function ModuloPLN({ 
  pacienteId, 
  defaultTab = 'transcripcion',
  hideOtherTabs = false 
}: ModuloPLNProps) {
  // Usar defaultTab como valor inicial
  // Si hideOtherTabs es true, ocultar las otras pestañas
}
```

### **Uso:**

```tsx
// Solo transcripción
<ModuloPLN 
  pacienteId={pacienteId} 
  defaultTab="transcripcion"
  hideOtherTabs={true}
/>

// Solo resumen
<ModuloPLN 
  pacienteId={pacienteId} 
  defaultTab="resumen"
  hideOtherTabs={true}
/>
```

---

## 🎨 **ESTILOS PERSONALIZADOS**

### **Cambiar colores del tema**

```tsx
// En ModuloPLN.tsx, personaliza los colores de las pestañas

<Tabs 
  defaultValue="transcripcion"
  sx={{
    '& .MuiTab-root': {
      color: '#667eea',
      '&.Mui-selected': {
        color: '#764ba2',
      }
    }
  }}
>
```

### **Agregar animaciones**

```tsx
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  <ModuloPLN pacienteId={pacienteId} />
</motion.div>
```

---

## 📱 **RESPONSIVE DESIGN**

El componente ya es responsive, pero puedes ajustar:

```tsx
<Dialog
  open={mostrarPLN}
  onClose={() => setMostrarPLN(false)}
  maxWidth="lg"
  fullWidth
  fullScreen={isMobile} // Pantalla completa en móvil
>
```

---

## 🔔 **NOTIFICACIONES Y FEEDBACK**

### **Agregar notificaciones de éxito**

```tsx
import { useSnackbar } from 'notistack';

const { enqueueSnackbar } = useSnackbar();

// Después de transcribir
enqueueSnackbar('Audio transcrito exitosamente', { variant: 'success' });

// Después de generar resumen
enqueueSnackbar('Resumen generado', { variant: 'success' });
```

---

## 🔄 **INTEGRACIÓN CON FORMULARIOS**

### **Pre-llenar formulario de consulta con transcripción**

```tsx
// En FormularioConsulta.tsx

const handleTranscripcionCompleta = (resultado: any) => {
  // Pre-llenar campos del formulario
  if (resultado.informacion_extraida) {
    const info = resultado.informacion_extraida;
    
    // Síntomas
    if (info.sintomas) {
      setFormulario(prev => ({
        ...prev,
        sintomas: info.sintomas.map(s => s.nombre).join(', ')
      }));
    }
    
    // Signos vitales
    if (info.signos_vitales) {
      setFormulario(prev => ({
        ...prev,
        presion_arterial: info.signos_vitales.presion_arterial,
        frecuencia_cardiaca: info.signos_vitales.frecuencia_cardiaca,
        temperatura: info.signos_vitales.temperatura
      }));
    }
    
    // Medicamentos
    if (info.medicamentos) {
      setMedicamentos(info.medicamentos);
    }
  }
  
  setMostrarTranscripcion(false);
  enqueueSnackbar('Formulario pre-llenado con datos de transcripción', { 
    variant: 'success' 
  });
};

// Pasar callback al componente
<ModuloPLN 
  pacienteId={pacienteId}
  onTranscripcionCompleta={handleTranscripcionCompleta}
/>
```

---

## 🔐 **PERMISOS Y ROLES**

### **Restringir acceso según rol**

```tsx
import { useAuth } from '@/contexts/AuthContext';

const { user } = useAuth();

// Solo mostrar a médicos
{user?.rol === 'medico' && (
  <Button onClick={() => setMostrarPLN(true)}>
    🧠 Módulo PLN
  </Button>
)}
```

---

## 📊 **ANALYTICS Y TRACKING**

### **Rastrear uso del módulo**

```tsx
import { trackEvent } from '@/utils/analytics';

// Al transcribir
trackEvent('PLN', 'Transcripción', 'Audio transcrito');

// Al generar resumen
trackEvent('PLN', 'Resumen', `Tipo: ${tipoResumen}`);

// Al traducir
trackEvent('PLN', 'Traducción', `${idiomaOrigen} → ${idiomaDestino}`);
```

---

## 🧪 **TESTING**

### **Ejemplo de test con React Testing Library**

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ModuloPLN from './ModuloPLN';

describe('ModuloPLN', () => {
  it('debe mostrar las 4 pestañas', () => {
    render(<ModuloPLN pacienteId="test-id" />);
    
    expect(screen.getByText('Transcripción')).toBeInTheDocument();
    expect(screen.getByText('Extracción')).toBeInTheDocument();
    expect(screen.getByText('Resumen')).toBeInTheDocument();
    expect(screen.getByText('Traducción')).toBeInTheDocument();
  });
  
  it('debe transcribir audio correctamente', async () => {
    render(<ModuloPLN pacienteId="test-id" />);
    
    const file = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
    const input = screen.getByLabelText('Subir archivo de audio');
    
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByText('Transcribir Audio'));
    
    await waitFor(() => {
      expect(screen.getByText(/Texto transcrito/i)).toBeInTheDocument();
    });
  });
});
```

---

## 📚 **DOCUMENTACIÓN ADICIONAL**

- **API Endpoints:** Ver `PRUEBAS_PLN_CURL.md`
- **Colección Postman:** Importar `DDX_PLN_Postman_Collection.json`
- **Documentación completa:** Ver `MODULO_PLN_DOCUMENTACION.md`

---

## 🎯 **EJEMPLO COMPLETO DE INTEGRACIÓN**

```tsx
// frontend/src/pages/PacienteDetalle.tsx

import React, { useState } from 'react';
import { 
  Container, 
  Paper, 
  Button, 
  Dialog, 
  DialogTitle, 
  DialogContent,
  IconButton 
} from '@mui/material';
import { Brain, Close } from '@mui/icons-material';
import ModuloPLN from '@/components/ModuloPLN';
import { useSnackbar } from 'notistack';

export default function PacienteDetalle() {
  const [mostrarPLN, setMostrarPLN] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  const pacienteId = "uuid-del-paciente"; // Obtener de useParams

  return (
    <Container maxWidth="xl">
      <Paper sx={{ p: 3 }}>
        {/* Otros botones del paciente */}
        
        <Button
          variant="contained"
          startIcon={<Brain />}
          onClick={() => setMostrarPLN(true)}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
            }
          }}
        >
          🧠 Módulo PLN
        </Button>
      </Paper>

      {/* Diálogo del módulo PLN */}
      <Dialog
        open={mostrarPLN}
        onClose={() => setMostrarPLN(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          🧠 Procesamiento de Lenguaje Natural
          <IconButton
            onClick={() => setMostrarPLN(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <ModuloPLN pacienteId={pacienteId} />
        </DialogContent>
      </Dialog>
    </Container>
  );
}
```

---

## ✅ **CHECKLIST DE INTEGRACIÓN**

- [ ] Importar componente `ModuloPLN`
- [ ] Agregar botón de acceso
- [ ] Configurar estado para mostrar/ocultar
- [ ] Agregar diálogo o página dedicada
- [ ] Pasar `pacienteId` como prop
- [ ] Configurar notificaciones (opcional)
- [ ] Agregar permisos por rol (opcional)
- [ ] Personalizar estilos (opcional)
- [ ] Integrar con formularios (opcional)
- [ ] Agregar analytics (opcional)
- [ ] Probar en diferentes dispositivos

---

## 🚀 **¡LISTO PARA USAR!**

El módulo PLN está completamente funcional y listo para integrarse en tu aplicación. Elige la opción que mejor se adapte a tu flujo de trabajo.
