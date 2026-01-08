import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import portalPacienteService from '../services/portalPacienteService';
import authService from '../services/authService';

export default function EstudiosScreen() {
  const [estudios, setEstudios] = useState([]);

  useEffect(() => {
    loadEstudios();
  }, []);

  const loadEstudios = async () => {
    const pacienteId = await authService.getPacienteId();
    if (pacienteId) {
      const data = await portalPacienteService.getSolicitudesEstudio(pacienteId);
      setEstudios(data);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <TouchableOpacity style={styles.addButton}>
        <Ionicons name="add-circle" size={24} color="#FFFFFF" />
        <Text style={styles.addButtonText}>Solicitar Estudio</Text>
      </TouchableOpacity>
      {estudios.map((estudio: any) => (
        <View key={estudio.id} style={styles.card}>
          <Text style={styles.title}>{estudio.nombre_estudio}</Text>
          <Text style={styles.subtitle}>{estudio.tipo_estudio}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC', padding: 16 },
  addButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0EA5E9', borderRadius: 12, padding: 16, marginBottom: 16 },
  addButtonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '600', marginLeft: 8 },
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  title: { fontSize: 18, fontWeight: '600', color: '#1E293B', marginBottom: 4 },
  subtitle: { fontSize: 14, color: '#64748B' },
});
