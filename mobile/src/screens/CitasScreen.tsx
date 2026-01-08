import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import portalPacienteService from '../services/portalPacienteService';
import authService from '../services/authService';

export default function CitasScreen() {
  const [citas, setCitas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadCitas();
  }, []);

  const loadCitas = async () => {
    try {
      const pacienteId = await authService.getPacienteId();
      if (pacienteId) {
        const data = await portalPacienteService.getCitas(pacienteId);
        setCitas(data);
      }
    } catch (error) {
      console.error('Error loading citas:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getStatusColor = (estado: string) => {
    const colors: any = {
      solicitada: '#F59E0B',
      confirmada: '#10B981',
      cancelada: '#EF4444',
      completada: '#6366F1',
    };
    return colors[estado] || '#94A3B8';
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadCitas} />}
    >
      <View style={styles.header}>
        <TouchableOpacity style={styles.addButton}>
          <Ionicons name="add-circle" size={24} color="#FFFFFF" />
          <Text style={styles.addButtonText}>Nueva Cita</Text>
        </TouchableOpacity>
      </View>

      {citas.map((cita: any) => (
        <View key={cita.id} style={styles.citaCard}>
          <View style={styles.citaHeader}>
            <Text style={styles.citaEspecialidad}>
              {cita.especialidad_solicitada || cita.tipo_cita}
            </Text>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor(cita.estado) }]}>
              <Text style={styles.statusText}>{cita.estado}</Text>
            </View>
          </View>
          <Text style={styles.citaMotivo}>{cita.motivo_consulta}</Text>
          <View style={styles.citaFooter}>
            <Ionicons name="calendar" size={16} color="#64748B" />
            <Text style={styles.citaDate}>
              {new Date(cita.fecha_solicitada).toLocaleDateString('es-MX')}
            </Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: { padding: 16, backgroundColor: '#FFFFFF' },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4F46E5',
    borderRadius: 12,
    padding: 16,
  },
  addButtonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '600', marginLeft: 8 },
  citaCard: {
    margin: 16,
    marginTop: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  citaHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  citaEspecialidad: { fontSize: 18, fontWeight: '600', color: '#1E293B' },
  statusBadge: { borderRadius: 12, paddingHorizontal: 12, paddingVertical: 4 },
  statusText: { color: '#FFFFFF', fontSize: 12, fontWeight: '600' },
  citaMotivo: { fontSize: 14, color: '#64748B', marginBottom: 12 },
  citaFooter: { flexDirection: 'row', alignItems: 'center' },
  citaDate: { fontSize: 14, color: '#64748B', marginLeft: 6 },
});
