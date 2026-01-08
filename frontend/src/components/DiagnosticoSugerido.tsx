/**
 * Componente para mostrar el diagnóstico sugerido por IA
 */
import { useState } from 'react';
import api from '@/lib/api';
import {
  Brain,
  AlertTriangle,
  CheckCircle,
  Activity,
  FileText,
  TrendingUp,
  Download
} from 'lucide-react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  LinearProgress
} from '@mui/material';

interface DiagnosticoSugeridoProps {
  pacienteId: string;
  onClose: () => void;
}

interface Diagnostico {
  nombre: string;
  codigo_cie10?: string;
  probabilidad: number;
  evidencia: string[];
  urgencia: 'bajo' | 'moderado' | 'alto' | 'critico';
}

interface ResultadoDiagnostico {
  diagnosticos: Diagnostico[];
  alertas: string[];
  recomendaciones_estudios: string[];
  recomendaciones_tratamiento: string[];
  resumen_clinico: string;
  datos_analizados: {
    consultas: number;
    laboratorios: number;
    estudios_ekg: number;
    estudios_eeg: number;
    ecografias: number;
  };
}

const DiagnosticoSugerido: React.FC<DiagnosticoSugeridoProps> = ({ pacienteId, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoDiagnostico | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleGenerar = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post(`/diagnosticos/sugerido/paciente/${pacienteId}`);
      setResultado(response.data);
      
    } catch (err: any) {
      console.error('Error al generar diagnóstico:', err);
      setError(err.response?.data?.detail || 'Error al generar el diagnóstico sugerido');
    } finally {
      setLoading(false);
    }
  };

  const handleDescargarPDF = async () => {
    try {
      setDownloadingPdf(true);
      
      const response = await api.post(
        `/diagnosticos/sugerido/paciente/${pacienteId}/pdf`,
        {},
        { responseType: 'blob' }
      );
      
      // Crear URL del blob y descargar
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `diagnostico_sugerido_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (err: any) {
      console.error('Error al descargar PDF:', err);
      setError('Error al generar el PDF');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const getUrgenciaColor = (urgencia: string) => {
    switch (urgencia) {
      case 'critico': return 'error';
      case 'alto': return 'warning';
      case 'moderado': return 'info';
      case 'bajo': return 'success';
      default: return 'default';
    }
  };

  const getUrgenciaLabel = (urgencia: string) => {
    switch (urgencia) {
      case 'critico': return 'CRÍTICO';
      case 'alto': return 'Alta';
      case 'moderado': return 'Moderada';
      case 'bajo': return 'Baja';
      default: return urgencia;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4">
      <div className="relative w-full max-w-4xl rounded-3xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-indigo-500" />
            <p className="text-lg font-semibold text-slate-900">Diagnóstico sugerido por IA</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-full border border-slate-200 p-1 text-slate-500 transition hover:text-slate-900"
          >
            <span className="sr-only">Cerrar</span>
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="max-h-[80vh] overflow-y-auto p-6">
          {error && (
            <div className="mb-3 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error}
            </div>
          )}

          {!resultado && !loading && (
            <div className="text-center py-8">
              <Brain className="mx-auto h-16 w-16 text-indigo-500" />
              <p className="mt-4 text-xl font-semibold text-slate-900">Análisis inteligente de diagnóstico</p>
              <p className="mt-2 text-sm text-slate-500">
                El sistema analizará toda la información disponible del paciente para generar un diagnóstico diferencial basado en evidencia.
              </p>
              <button
                onClick={handleGenerar}
                disabled={loading}
                className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:shadow-2xl disabled:opacity-60"
              >
                <Brain className="h-4 w-4" /> Generar diagnóstico sugerido
              </button>
            </div>
          )}

          {loading && (
            <div className="text-center py-8">
              <div className="mx-auto mb-3 h-12 w-12 animate-spin rounded-full border-4 border-indigo-100 border-t-indigo-500"></div>
              <p className="text-lg font-semibold text-slate-900">Analizando información del paciente…</p>
              <p className="text-sm text-slate-500">Esto puede tomar unos segundos</p>
            </div>
          )}

          {resultado && !loading && (
            <div className="space-y-4">
            {/* Datos Analizados */}
            <Card sx={{ mb: 3, bgcolor: '#f3f4f6' }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  📊 Datos Analizados
                </Typography>
                <Box display="flex" gap={2} flexWrap="wrap">
                  <Chip label={`${resultado.datos_analizados.consultas} Consulta(s)`} size="small" />
                  <Chip label={`${resultado.datos_analizados.laboratorios} Laboratorio(s)`} size="small" />
                  <Chip label={`${resultado.datos_analizados.estudios_ekg} EKG(s)`} size="small" />
                  <Chip label={`${resultado.datos_analizados.estudios_eeg} EEG(s)`} size="small" />
                  <Chip label={`${resultado.datos_analizados.ecografias} Ecografía(s)`} size="small" />
                </Box>
              </CardContent>
            </Card>

            {/* Resumen Clínico */}
            {resultado.resumen_clinico && (
              <Alert severity="info" icon={<FileText size={20} />} sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <strong>Resumen Clínico</strong>
                </Typography>
                <Typography variant="body2">{resultado.resumen_clinico}</Typography>
              </Alert>
            )}

            {/* Alertas */}
            {resultado.alertas && resultado.alertas.length > 0 && (
              <Alert severity="warning" icon={<AlertTriangle size={20} />} sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <strong>⚠️ Alertas Clínicas</strong>
                </Typography>
                <List dense>
                  {resultado.alertas.map((alerta, index) => (
                    <ListItem key={index} sx={{ py: 0 }}>
                      <ListItemText primary={`• ${alerta}`} />
                    </ListItem>
                  ))}
                </List>
              </Alert>
            )}

            {/* Diagnósticos Diferenciales */}
            <Typography variant="h6" gutterBottom sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Activity size={20} />
              Diagnósticos Diferenciales
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              {resultado.diagnosticos.map((diagnostico, index) => (
                <Grid item xs={12} key={index}>
                  <Card
                    sx={{
                      border: index === 0 ? '2px solid #9333ea' : '1px solid #e5e7eb',
                      position: 'relative'
                    }}
                  >
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                        <Box flex={1}>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            {index === 0 && (
                              <Chip
                                label="Más Probable"
                                size="small"
                                sx={{
                                  bgcolor: '#9333ea',
                                  color: 'white',
                                  fontWeight: 'bold'
                                }}
                              />
                            )}
                            <Typography variant="h6" component="span">
                              {index + 1}. {diagnostico.nombre}
                            </Typography>
                          </Box>
                          {diagnostico.codigo_cie10 && (
                            <Typography variant="caption" color="text.secondary">
                              CIE-10: {diagnostico.codigo_cie10}
                            </Typography>
                          )}
                        </Box>
                        <Box textAlign="right">
                          <Typography variant="h5" color="primary" fontWeight="bold">
                            {diagnostico.probabilidad}%
                          </Typography>
                          <Chip
                            label={getUrgenciaLabel(diagnostico.urgencia)}
                            size="small"
                            color={getUrgenciaColor(diagnostico.urgencia)}
                          />
                        </Box>
                      </Box>

                      <Box mb={2}>
                        <LinearProgress
                          variant="determinate"
                          value={diagnostico.probabilidad}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            bgcolor: '#e5e7eb',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: index === 0 ? '#9333ea' : '#6b7280'
                            }
                          }}
                        />
                      </Box>

                      <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                        <strong>📋 Evidencia:</strong>
                      </Typography>
                      <List dense>
                        {diagnostico.evidencia.map((evidencia, idx) => (
                          <ListItem key={idx} sx={{ py: 0.5 }}>
                            <CheckCircle size={16} style={{ marginRight: 8, color: '#10b981' }} />
                            <ListItemText primary={evidencia} />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {/* Recomendaciones */}
            <Box mt={4}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp size={20} />
                Recomendaciones
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                {resultado.recomendaciones_estudios && resultado.recomendaciones_estudios.length > 0 && (
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                          🔬 Estudios Adicionales
                        </Typography>
                        <List dense>
                          {resultado.recomendaciones_estudios.map((estudio, index) => (
                            <ListItem key={index} sx={{ py: 0.5 }}>
                              <ListItemText primary={`• ${estudio}`} />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {resultado.recomendaciones_tratamiento && resultado.recomendaciones_tratamiento.length > 0 && (
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                          💊 Tratamiento y Seguimiento
                        </Typography>
                        <List dense>
                          {resultado.recomendaciones_tratamiento.map((tratamiento, index) => (
                            <ListItem key={index} sx={{ py: 0.5 }}>
                              <ListItemText primary={`• ${tratamiento}`} />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            </Box>

            {/* Disclaimer */}
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="caption">
                <strong>Nota:</strong> Este diagnóstico es una sugerencia generada por IA basada en la información disponible.
                Debe ser revisado y confirmado por el médico tratante considerando el contexto clínico completo del paciente.
              </Typography>
            </Alert>
          </div>
        )}
        </div>

        <div className="flex flex-wrap items-center justify-end gap-3 border-t border-slate-100 px-6 py-4">
          <button
            onClick={onClose}
            className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
          >
            Cerrar
          </button>
          {resultado && (
            <>
              <button
                onClick={handleDescargarPDF}
                disabled={downloadingPdf}
                className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-green-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition hover:shadow-2xl disabled:opacity-60"
              >
                <Download className="h-4 w-4" /> {downloadingPdf ? 'Generando PDF…' : 'Descargar PDF'}
              </button>
              <button
                onClick={handleGenerar}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-2xl border border-indigo-200 px-4 py-2 text-sm font-semibold text-indigo-600 transition hover:border-indigo-300 hover:bg-indigo-50 disabled:opacity-60"
              >
                <Brain className="h-4 w-4" /> Regenerar análisis
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};


export default DiagnosticoSugerido;
