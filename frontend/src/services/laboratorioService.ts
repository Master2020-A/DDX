/**
 * Servicio para gestión de laboratorios clínicos
 */
import api from '@/lib/api';
import {
  PruebaLaboratorio,
  PruebaLaboratorioResumen,
  CrearPruebaLaboratorio,
  RangoReferencia
} from '@/types/laboratorio';

class LaboratorioService {
  /**
   * Crear nueva prueba de laboratorio
   */
  async crearPrueba(data: CrearPruebaLaboratorio): Promise<PruebaLaboratorio> {
    const response = await api.post('/laboratorio/', data);
    return response.data;
  }

  /**
   * Listar pruebas de un paciente
   */
  async listarPruebasPaciente(
    pacienteId: string,
    area?: string
  ): Promise<PruebaLaboratorioResumen[]> {
    const params = area ? { area } : {};
    const response = await api.get(`/laboratorio/paciente/${pacienteId}`, { params });
    return response.data;
  }

  /**
   * Obtener detalle de una prueba
   */
  async obtenerPrueba(pruebaId: string): Promise<PruebaLaboratorio> {
    const response = await api.get(`/laboratorio/${pruebaId}`);
    return response.data;
  }

  /**
   * Obtener rangos de referencia por área
   */
  async obtenerRangos(area: string): Promise<RangoReferencia[]> {
    const response = await api.get(`/laboratorio/rangos/area/${area}`);
    return response.data;
  }

  /**
   * Obtener todos los rangos de referencia del catálogo
   */
  async obtenerRangosReferencia(): Promise<RangoReferencia[]> {
    const response = await api.get('/laboratorio/rangos/');
    return response.data;
  }

  /**
   * Actualizar prueba de laboratorio
   */
  async actualizarPrueba(
    pruebaId: string,
    data: Partial<CrearPruebaLaboratorio>
  ): Promise<{ mensaje: string; id: string }> {
    const response = await api.put(`/laboratorio/${pruebaId}`, data);
    return response.data;
  }

  /**
   * Extraer datos desde archivo PDF o imagen
   */
  async extraerDesdeArchivo(
    archivo: File,
    pacienteId: string,
    consultaId?: string,
    laboratorioExterno?: string
  ): Promise<any> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('paciente_id', pacienteId);
    if (consultaId) formData.append('consulta_id', consultaId);
    if (laboratorioExterno) formData.append('laboratorio_externo', laboratorioExterno);

    const response = await api.post('/laboratorio/extraer-desde-archivo/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  /**
   * Extraer datos y crear prueba automáticamente desde archivo
   */
  async extraerYCrearDesdeArchivo(
    archivo: File,
    pacienteId: string,
    consultaId?: string,
    laboratorioExterno?: string,
    numeroOrden?: string,
    notasMedico?: string
  ): Promise<PruebaLaboratorio> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('paciente_id', pacienteId);
    if (consultaId) formData.append('consulta_id', consultaId);
    if (laboratorioExterno) formData.append('laboratorio_externo', laboratorioExterno);
    if (numeroOrden) formData.append('numero_orden', numeroOrden);
    if (notasMedico) formData.append('notas_medico', notasMedico);

    const response = await api.post('/laboratorio/extraer-y-crear-desde-archivo/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  /**
   * Descargar PDF de una prueba de laboratorio
   */
  async descargarPDF(pruebaId: string): Promise<Blob> {
    const response = await api.get(`/laboratorio/${pruebaId}/pdf`, {
      responseType: 'blob'
    });
    return response.data;
  }
}

export default new LaboratorioService();
