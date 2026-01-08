import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Activity,
  Beaker,
  TrendingUp,
  BarChart3,
  FileText
} from 'lucide-react';

const FHIRObservations: React.FC = () => {
  const { pacienteId } = useParams<{ pacienteId: string }>();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carga de datos
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, [pacienteId]);

  const stats = {
    total: 0,
    vitalsCount: 0,
    labsCount: 0,
    normal: 0,
    abnormal: 0
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" py={8}>
          <CircularProgress size={60} />
          <Typography variant="body1" color="text.secondary" mt={2}>
            Cargando observaciones FHIR...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Encabezado */}
      <Box mb={4}>
        <Box display="flex" alignItems="center" gap={2} mb={1}>
          <FileText size={32} color="#9333ea" />
          <Typography variant="h4" component="h1" fontWeight="bold">
            Observaciones FHIR
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Recursos de observación según estándar HL7 FHIR R4
        </Typography>
      </Box>

      {/* Estadísticas */}
      <Grid container spacing={2} mb={4}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Total Observaciones
              </Typography>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h4" fontWeight="bold">{stats.total}</Typography>
                <BarChart3 size={32} color="#9ca3af" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Signos Vitales
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-blue-600">{stats.vitalsCount}</span>
              <Activity className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Laboratorio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-purple-600">{stats.labsCount}</span>
              <Beaker className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Normales
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-green-600">{stats.normal}</span>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                {stats.total > 0 ? Math.round((stats.normal / stats.total) * 100) : 0}%
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Anormales
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-orange-600">{stats.abnormal}</span>
              <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                {stats.total > 0 ? Math.round((stats.abnormal / stats.total) * 100) : 0}%
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pestañas */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Todas ({stats.total})
          </TabsTrigger>
          <TabsTrigger value="vital-signs" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Signos Vitales ({stats.vitalsCount})
          </TabsTrigger>
          <TabsTrigger value="laboratory" className="flex items-center gap-2">
            <Beaker className="h-4 w-4" />
            Laboratorio ({stats.labsCount})
          </TabsTrigger>
          <TabsTrigger value="trends" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Tendencias
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <ObservationList patientId={pacienteId!} showFilters={true} />
        </TabsContent>

        <TabsContent value="vital-signs" className="space-y-4">
          <ObservationList patientId={pacienteId!} category="vital-signs" showFilters={false} />
        </TabsContent>

        <TabsContent value="laboratory" className="space-y-4">
          <ObservationList patientId={pacienteId!} category="laboratory" showFilters={false} />
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <ObservationTrends observations={allObservations} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FHIRObservations;
