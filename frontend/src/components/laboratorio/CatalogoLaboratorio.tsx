/**
 * Componente para visualizar el catálogo completo de laboratorio
 * Permite ver todos los parámetros con sus rangos de referencia
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  InputAdornment,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  MenuItem
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  Male as MaleIcon,
  Female as FemaleIcon,
  ChildCare as ChildIcon,
  PregnantWoman as PregnantIcon
} from '@mui/icons-material';
import laboratorioService from '@/services/laboratorioService';
import { RangoReferencia } from '@/types/laboratorio';

interface CatalogoLaboratorioProps {
  onSeleccionarParametro?: (parametro: RangoReferencia) => void;
}

const CatalogoLaboratorio: React.FC<CatalogoLaboratorioProps> = ({
  onSeleccionarParametro
}) => {
  const [rangos, setRangos] = useState<RangoReferencia[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busqueda, setBusqueda] = useState('');
  const [areaFiltro, setAreaFiltro] = useState<string>('todas');
  const [grupoEtarioFiltro, setGrupoEtarioFiltro] = useState<string>('todos');

  useEffect(() => {
    cargarCatalogo();
  }, []);

  const cargarCatalogo = async () => {
    setLoading(true);
    setError(null);
    try {
      // Obtener todos los rangos de referencia
      const response = await laboratorioService.obtenerRangosReferencia();
      setRangos(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar catálogo');
    } finally {
      setLoading(false);
    }
  };

  // Agrupar rangos por área y tipo de prueba
  const rangosPorArea = rangos.reduce((acc, rango) => {
    const area = rango.area || 'sin_area';
    if (!acc[area]) {
      acc[area] = {};
    }
    const tipoPrueba = rango.tipo_prueba || 'sin_tipo';
    if (!acc[area][tipoPrueba]) {
      acc[area][tipoPrueba] = [];
    }
    acc[area][tipoPrueba].push(rango);
    return acc;
  }, {} as Record<string, Record<string, RangoReferencia[]>>);

  // Filtrar rangos
  const rangosFiltrados = rangos.filter(rango => {
    const matchBusqueda = busqueda === '' || 
      rango.parametro.toLowerCase().includes(busqueda.toLowerCase()) ||
      rango.nombre_completo?.toLowerCase().includes(busqueda.toLowerCase());
    
    const matchArea = areaFiltro === 'todas' || rango.area === areaFiltro;
    
    const matchGrupoEtario = grupoEtarioFiltro === 'todos' || 
      rango.grupo_etario === grupoEtarioFiltro ||
      (!rango.grupo_etario && grupoEtarioFiltro === 'adulto');
    
    return matchBusqueda && matchArea && matchGrupoEtario;
  });

  const obtenerNombreArea = (area: string): string => {
    const nombres: Record<string, string> = {
      'hematologia': '🩸 Hematología',
      'quimica_clinica': '🧪 Química Clínica',
      'inmunologia': '🛡️ Inmunología',
      'uroanalisis': '💧 Uroanálisis'
    };
    return nombres[area] || area;
  };

  const obtenerNombreTipoPrueba = (tipo: string): string => {
    const nombres: Record<string, string> = {
      'biometria_hematica': 'Biometría Hemática Completa',
      'glucosa': 'Glucosa en Ayunas',
      'funcion_renal': 'Perfil de Función Renal',
      'perfil_lipidico': 'Perfil Lipídico',
      'funcion_hepatica': 'Perfil de Función Hepática',
      'electrolitos': 'Electrolitos Séricos',
      'marcadores_inflamatorios': 'Marcadores Inflamatorios'
    };
    return nombres[tipo] || tipo;
  };

  const obtenerIconoSexo = (sexo?: string) => {
    if (sexo === 'M') return <MaleIcon fontSize="small" color="primary" />;
    if (sexo === 'F') return <FemaleIcon fontSize="small" color="secondary" />;
    return null;
  };

  const obtenerChipGrupoEtario = (grupo?: string) => {
    if (!grupo) return <Chip label="Adulto" size="small" />;
    
    const configs: Record<string, { label: string; color: any; icon?: any }> = {
      'recien_nacido': { label: 'Recién Nacido', color: 'info', icon: <ChildIcon /> },
      'pediatrico': { label: 'Pediátrico', color: 'success', icon: <ChildIcon /> },
      'adolescente': { label: 'Adolescente', color: 'warning' },
      'adulto': { label: 'Adulto', color: 'default' },
      'embarazo': { label: 'Embarazo', color: 'secondary', icon: <PregnantIcon /> }
    };
    
    const config = configs[grupo] || { label: grupo, color: 'default' };
    return <Chip label={config.label} size="small" color={config.color} icon={config.icon} />;
  };

  const estadisticas = {
    total: rangos.length,
    parametrosUnicos: new Set(rangos.map(r => r.parametro)).size,
    areas: Object.keys(rangosPorArea).length,
    tiposPruebas: Object.values(rangosPorArea).reduce((acc, tipos) => acc + Object.keys(tipos).length, 0)
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      {/* Encabezado con estadísticas */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          📚 Catálogo de Laboratorio Clínico
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Rangos de referencia diferenciados por sexo y edad
        </Typography>
        
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="primary">{estadisticas.total}</Typography>
                <Typography variant="body2" color="text.secondary">Rangos Totales</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="secondary">{estadisticas.parametrosUnicos}</Typography>
                <Typography variant="body2" color="text.secondary">Parámetros Únicos</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="success.main">{estadisticas.areas}</Typography>
                <Typography variant="body2" color="text.secondary">Áreas</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="warning.main">{estadisticas.tiposPruebas}</Typography>
                <Typography variant="body2" color="text.secondary">Tipos de Pruebas</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Buscar parámetro..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              select
              label="Área"
              value={areaFiltro}
              onChange={(e) => setAreaFiltro(e.target.value)}
            >
              <MenuItem value="todas">Todas las áreas</MenuItem>
              <MenuItem value="hematologia">🩸 Hematología</MenuItem>
              <MenuItem value="quimica_clinica">🧪 Química Clínica</MenuItem>
              <MenuItem value="inmunologia">🛡️ Inmunología</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              select
              label="Grupo Etario"
              value={grupoEtarioFiltro}
              onChange={(e) => setGrupoEtarioFiltro(e.target.value)}
            >
              <MenuItem value="todos">Todos los grupos</MenuItem>
              <MenuItem value="recien_nacido">Recién Nacido</MenuItem>
              <MenuItem value="pediatrico">Pediátrico</MenuItem>
              <MenuItem value="adolescente">Adolescente</MenuItem>
              <MenuItem value="adulto">Adulto</MenuItem>
              <MenuItem value="embarazo">Embarazo</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Catálogo por áreas */}
      {Object.entries(rangosPorArea).map(([area, tiposPruebas]) => (
        <Accordion key={area} defaultExpanded={area === 'hematologia'}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">{obtenerNombreArea(area)}</Typography>
            <Chip 
              label={Object.values(tiposPruebas).reduce((acc, rangos) => acc + rangos.length, 0)} 
              size="small" 
              sx={{ ml: 2 }}
            />
          </AccordionSummary>
          <AccordionDetails>
            {Object.entries(tiposPruebas).map(([tipoPrueba, rangosParametros]) => {
              // Filtrar rangos de este tipo de prueba
              const rangosFiltradosTipo = rangosParametros.filter(rango => {
                const matchBusqueda = busqueda === '' || 
                  rango.parametro.toLowerCase().includes(busqueda.toLowerCase()) ||
                  rango.nombre_completo?.toLowerCase().includes(busqueda.toLowerCase());
                
                const matchGrupoEtario = grupoEtarioFiltro === 'todos' || 
                  rango.grupo_etario === grupoEtarioFiltro ||
                  (!rango.grupo_etario && grupoEtarioFiltro === 'adulto');
                
                return matchBusqueda && matchGrupoEtario;
              });

              if (rangosFiltradosTipo.length === 0) return null;

              return (
                <Box key={tipoPrueba} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                    {obtenerNombreTipoPrueba(tipoPrueba)}
                  </Typography>
                  
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell><strong>Parámetro</strong></TableCell>
                          <TableCell><strong>Sexo</strong></TableCell>
                          <TableCell><strong>Grupo</strong></TableCell>
                          <TableCell align="right"><strong>Mínimo</strong></TableCell>
                          <TableCell align="right"><strong>Máximo</strong></TableCell>
                          <TableCell><strong>Unidad</strong></TableCell>
                          <TableCell><strong>Descripción</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {rangosFiltradosTipo.map((rango, idx) => (
                          <TableRow 
                            key={idx}
                            hover
                            onClick={() => onSeleccionarParametro?.(rango)}
                            sx={{ cursor: onSeleccionarParametro ? 'pointer' : 'default' }}
                          >
                            <TableCell>
                              <Typography variant="body2" fontWeight="medium">
                                {rango.nombre_completo || rango.parametro}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {rango.parametro}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              {obtenerIconoSexo(rango.sexo)}
                              {rango.sexo && (
                                <Typography variant="caption" sx={{ ml: 0.5 }}>
                                  {rango.sexo === 'M' ? 'Hombre' : 'Mujer'}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell>
                              {obtenerChipGrupoEtario(rango.grupo_etario)}
                            </TableCell>
                            <TableCell align="right">
                              {rango.valor_min?.toFixed(1) || '-'}
                              {rango.critico_bajo && (
                                <Typography variant="caption" color="error" display="block">
                                  ⚠️ {rango.critico_bajo}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell align="right">
                              {rango.valor_max?.toFixed(1) || '-'}
                              {rango.critico_alto && (
                                <Typography variant="caption" color="error" display="block">
                                  ⚠️ {rango.critico_alto}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell>
                              <Chip label={rango.unidad} size="small" variant="outlined" />
                            </TableCell>
                            <TableCell>
                              <Typography variant="caption">
                                {rango.descripcion || '-'}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              );
            })}
          </AccordionDetails>
        </Accordion>
      ))}

      {rangosFiltrados.length === 0 && (
        <Alert severity="info">
          No se encontraron parámetros con los filtros seleccionados
        </Alert>
      )}
    </Box>
  );
};

export default CatalogoLaboratorio;
