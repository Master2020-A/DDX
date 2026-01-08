import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, Switch, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import portalPacienteService from '../services/portalPacienteService';
import authService from '../services/authService';

export default function ConfiguracionScreen({ navigation }: any) {
  const [config, setConfig] = useState<any>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    const pacienteId = await authService.getPacienteId();
    if (pacienteId) {
      const data = await portalPacienteService.getConfiguracion(pacienteId);
      setConfig(data);
    }
  };

  const handleToggle = async (key: string, value: boolean) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    const pacienteId = await authService.getPacienteId();
    if (pacienteId) {
      await portalPacienteService.actualizarConfiguracion(pacienteId, newConfig);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Cerrar Sesión',
      '¿Estás seguro que deseas cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar Sesión',
          style: 'destructive',
          onPress: async () => {
            await authService.logout();
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  if (!config) return null;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notificaciones</Text>
        {[
          { label: 'Email', key: 'notificaciones_email' },
          { label: 'SMS', key: 'notificaciones_sms' },
          { label: 'Push', key: 'notificaciones_push' },
        ].map(({ label, key }) => (
          <View key={key} style={styles.row}>
            <Text style={styles.label}>{label}</Text>
            <Switch
              value={config[key]}
              onValueChange={(value) => handleToggle(key, value)}
              trackColor={{ false: '#CBD5E1', true: '#4F46E5' }}
              thumbColor="#FFFFFF"
            />
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recordatorios</Text>
        {[
          { label: 'Citas', key: 'recordatorios_citas' },
          { label: 'Medicamentos', key: 'recordatorios_medicamentos' },
          { label: 'Estudios', key: 'recordatorios_estudios' },
        ].map(({ label, key }) => (
          <View key={key} style={styles.row}>
            <Text style={styles.label}>{label}</Text>
            <Switch
              value={config[key]}
              onValueChange={(value) => handleToggle(key, value)}
              trackColor={{ false: '#CBD5E1', true: '#4F46E5' }}
              thumbColor="#FFFFFF"
            />
          </View>
        ))}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Ionicons name="log-out" size={24} color="#EF4444" />
        <Text style={styles.logoutText}>Cerrar Sesión</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  section: { backgroundColor: '#FFFFFF', marginTop: 16, padding: 16 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#1E293B', marginBottom: 16 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#E2E8F0' },
  label: { fontSize: 16, color: '#1E293B' },
  logoutButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#FFFFFF', margin: 16, padding: 16, borderRadius: 12, borderWidth: 2, borderColor: '#EF4444' },
  logoutText: { fontSize: 16, fontWeight: '600', color: '#EF4444', marginLeft: 8 },
});
