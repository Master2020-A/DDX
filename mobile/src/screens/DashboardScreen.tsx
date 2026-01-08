import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import portalPacienteService from '../services/portalPacienteService';
import authService from '../services/authService';

export default function DashboardScreen({ navigation }: any) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState<any>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const pacienteId = await authService.getPacienteId();
      if (pacienteId) {
        const data = await portalPacienteService.getDashboard(pacienteId);
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  const metrics = [
    {
      label: 'Citas pendientes',
      value: dashboardData?.citas_pendientes || 0,
      icon: 'calendar',
      color: '#4F46E5',
    },
    {
      label: 'Estudios pendientes',
      value: dashboardData?.estudios_pendientes || 0,
      icon: 'document-text',
      color: '#0EA5E9',
    },
    {
      label: 'Mensajes sin leer',
      value: dashboardData?.mensajes_sin_leer || 0,
      icon: 'chatbubbles',
      color: '#06B6D4',
    },
    {
      label: 'Recordatorios activos',
      value: dashboardData?.recordatorios_activos || 0,
      icon: 'notifications',
      color: '#8B5CF6',
    },
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.greeting}>¡Hola!</Text>
        <Text style={styles.subtitle}>Bienvenido a tu Portal de Salud</Text>
      </View>

      <View style={styles.metricsGrid}>
        {metrics.map((metric, index) => (
          <View key={index} style={[styles.metricCard, { borderLeftColor: metric.color }]}>
            <Ionicons name={metric.icon as any} size={24} color={metric.color} />
            <Text style={styles.metricValue}>{metric.value}</Text>
            <Text style={styles.metricLabel}>{metric.label}</Text>
          </View>
        ))}
      </View>

      {dashboardData?.proxima_cita && (
        <View style={styles.nextAppointment}>
          <View style={styles.appointmentHeader}>
            <Ionicons name="calendar" size={24} color="#4F46E5" />
            <Text style={styles.appointmentTitle}>Próxima Cita</Text>
          </View>
          <Text style={styles.appointmentSpecialty}>
            {dashboardData.proxima_cita.especialidad_solicitada || dashboardData.proxima_cita.tipo_cita}
          </Text>
          <Text style={styles.appointmentReason}>
            {dashboardData.proxima_cita.motivo_consulta}
          </Text>
          <View style={styles.appointmentDate}>
            <Ionicons name="time" size={16} color="#64748B" />
            <Text style={styles.appointmentDateText}>
              {new Date(dashboardData.proxima_cita.fecha_solicitada).toLocaleDateString('es-MX')}
              {dashboardData.proxima_cita.hora_solicitada && ` - ${dashboardData.proxima_cita.hora_solicitada}`}
            </Text>
          </View>
        </View>
      )}

      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Acciones Rápidas</Text>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Citas')}
        >
          <Ionicons name="add-circle" size={24} color="#4F46E5" />
          <Text style={styles.actionButtonText}>Nueva Cita</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Estudios')}
        >
          <Ionicons name="add-circle" size={24} color="#0EA5E9" />
          <Text style={styles.actionButtonText}>Solicitar Estudio</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Mensajes')}
        >
          <Ionicons name="add-circle" size={24} color="#06B6D4" />
          <Text style={styles.actionButtonText}>Enviar Mensaje</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
  },
  header: {
    padding: 24,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  subtitle: {
    fontSize: 16,
    color: '#64748B',
    marginTop: 4,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  metricCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  metricValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1E293B',
    marginTop: 8,
  },
  metricLabel: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 4,
  },
  nextAppointment: {
    margin: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  appointmentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  appointmentTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginLeft: 8,
  },
  appointmentSpecialty: {
    fontSize: 20,
    fontWeight: '600',
    color: '#4F46E5',
    marginBottom: 8,
  },
  appointmentReason: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 12,
  },
  appointmentDate: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  appointmentDateText: {
    fontSize: 14,
    color: '#64748B',
    marginLeft: 6,
  },
  quickActions: {
    margin: 16,
    marginTop: 0,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
    marginLeft: 12,
  },
});
