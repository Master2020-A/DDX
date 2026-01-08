import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Pacientes from './pages/Pacientes'
import PacienteDetalle from './pages/PacienteDetalle'
import NuevaConsulta from './pages/NuevaConsulta'
import ConsultaDetalle from './pages/ConsultaDetalle'
import HistoriaClinica from './pages/HistoriaClinica'
import ListaHistoriasClinicas from './pages/ListaHistoriasClinicas'
import VerHistoriaClinica from './pages/VerHistoriaClinica'
import ExpedienteClinico from './pages/ExpedienteClinico'
import Consultas from './pages/Consultas'
import Reportes from './pages/Reportes'
import ImagenesMedicas from './pages/ImagenesMedicas'
import GaleriaImagenes from './pages/GaleriaImagenes'
import VisorImagenes from './pages/VisorImagenes'
import ComparadorImagenes from './pages/ComparadorImagenes'
import Laboratorios from './pages/Laboratorios'
import EstudiosEspeciales from './pages/EstudiosEspeciales'
import Hospitalizacion from './pages/Hospitalizacion'
import Interconsultas from './pages/Interconsultas'
import PreDiagnostico from './pages/PreDiagnostico'
import Analytics from './pages/Analytics'
import Admin from './pages/Admin'
import CumplimientoNormativo from './pages/CumplimientoNormativo'
import BackupsRecuperacion from './pages/BackupsRecuperacion'
import AplicacionMovil from './pages/AplicacionMovil'
import Integraciones from './pages/Integraciones'
import APIPublica from './pages/APIPublica'
import InteligenciaArtificial from './pages/InteligenciaArtificial'
import SalaTelemedicina from './pages/SalaTelemedicina'
import Telemedicina from './pages/Telemedicina'
import PanelInteroperabilidadFHIR from './components/ia-medica/PanelInteroperabilidadFHIR'
import PortalPaciente from './pages/PortalPacienteTailwind'
import MultiTenancy from './pages/MultiTenancy'
import Interoperabilidad from './pages/Interoperabilidad'
import FHIRObservations from './pages/FHIRObservationsSimple'
import FHIRImport from './pages/FHIRImport'
import DDXStudioNew from './pages/DDXStudioNew'
import Workflows from './pages/WorkflowsNew'
import Marketplace from './pages/Marketplace'
import N8NIntegration from './pages/N8NIntegration'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/telemedicina/sala/:consultaId" element={<ProtectedRoute><SalaTelemedicina /></ProtectedRoute>} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="pacientes" element={<Pacientes />} />
          <Route path="pacientes/:id" element={<PacienteDetalle />} />
          <Route path="consultas" element={<Consultas />} />
          <Route path="consultas/nueva/:pacienteId" element={<NuevaConsulta />} />
          <Route path="consultas/:id" element={<ConsultaDetalle />} />
          <Route path="reportes" element={<Reportes />} />
          <Route path="historia-clinica/:pacienteId" element={<HistoriaClinica />} />
          <Route path="historias-clinicas/:pacienteId" element={<ListaHistoriasClinicas />} />
          <Route path="historia-clinica/ver/:id" element={<VerHistoriaClinica />} />
          <Route path="expediente/:pacienteId" element={<ExpedienteClinico />} />
          <Route path="imagenes" element={<ImagenesMedicas />} />
          <Route path="imagenes/:pacienteId" element={<GaleriaImagenes />} />
          <Route path="imagenes/:imagenId/visor" element={<VisorImagenes />} />
          <Route path="comparador/:imagen1Id/:imagen2Id" element={<ComparadorImagenes />} />
          <Route path="laboratorios/:pacienteId" element={<Laboratorios />} />
          <Route path="estudios-especiales/:pacienteId" element={<EstudiosEspeciales />} />
          <Route path="hospitalizacion" element={<Hospitalizacion />} />
          <Route path="interconsultas" element={<Interconsultas />} />
          <Route path="prediagnostico" element={<PreDiagnostico />} />
          <Route path="ia-medica" element={<InteligenciaArtificial />} />
          <Route path="telemedicina" element={<Telemedicina />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="admin" element={<Admin />} />
          <Route path="cumplimiento" element={<CumplimientoNormativo />} />
          <Route path="backups" element={<BackupsRecuperacion />} />
          <Route path="app-movil" element={<AplicacionMovil />} />
          <Route path="integraciones" element={<Integraciones />} />
          <Route path="api-publica" element={<APIPublica />} />
          <Route path="ia/interoperabilidad" element={<PanelInteroperabilidadFHIR />} />
          <Route path="portal-paciente" element={<PortalPaciente />} />
          <Route path="multi-tenancy" element={<MultiTenancy />} />
          <Route path="interoperabilidad" element={<Interoperabilidad />} />
          <Route path="fhir-observations" element={<FHIRObservations />} />
          <Route path="pacientes/:pacienteId/fhir-observations" element={<FHIRObservations />} />
          <Route path="fhir-import" element={<FHIRImport />} />
          <Route path="pacientes/:pacienteId/fhir-import" element={<FHIRImport />} />
          <Route path="ddx-studio" element={<DDXStudioNew />} />
          <Route path="workflows" element={<Workflows />} />
          <Route path="marketplace" element={<Marketplace />} />
          <Route path="n8n" element={<N8NIntegration />} />
        </Route>
      </Routes>
    </Router>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuthStore()
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

export default App
