import { Button } from '@/components/ui/button';
import { FileDown, Loader2 } from 'lucide-react';
import { useState } from 'react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { CitaPaciente, SolicitudEstudio, RecordatorioMedicamento } from '@/services/portalPacienteService';

interface ExportarPDFProps {
  tipo: 'citas' | 'estudios' | 'recordatorios';
  datos: CitaPaciente[] | SolicitudEstudio[] | RecordatorioMedicamento[];
  titulo: string;
}

export default function ExportarPDF({ tipo, datos, titulo }: ExportarPDFProps) {
  const [exportando, setExportando] = useState(false);

  const exportarCitas = (doc: jsPDF, citas: CitaPaciente[]) => {
    const tableData = citas.map(cita => [
      format(new Date(cita.fecha_solicitada), 'PP', { locale: es }),
      cita.hora_solicitada || 'Sin hora',
      cita.especialidad_solicitada || cita.tipo_cita,
      cita.motivo_consulta.substring(0, 50) + (cita.motivo_consulta.length > 50 ? '...' : ''),
      cita.estado.toUpperCase(),
    ]);

    autoTable(doc, {
      head: [['Fecha', 'Hora', 'Especialidad', 'Motivo', 'Estado']],
      body: tableData,
      startY: 40,
      styles: { fontSize: 9 },
      headStyles: { fillColor: [59, 130, 246] },
    });
  };

  const exportarEstudios = (doc: jsPDF, estudios: SolicitudEstudio[]) => {
    const tableData = estudios.map(estudio => [
      format(new Date(estudio.fecha_solicitud), 'PP', { locale: es }),
      estudio.tipo_estudio.toUpperCase(),
      estudio.nombre_estudio,
      estudio.prioridad || 'Normal',
      estudio.estado.toUpperCase(),
      estudio.resultado_disponible ? 'Sí' : 'No',
    ]);

    autoTable(doc, {
      head: [['Fecha', 'Tipo', 'Estudio', 'Prioridad', 'Estado', 'Resultado']],
      body: tableData,
      startY: 40,
      styles: { fontSize: 9 },
      headStyles: { fillColor: [59, 130, 246] },
    });
  };

  const exportarRecordatorios = (doc: jsPDF, recordatorios: RecordatorioMedicamento[]) => {
    const tableData = recordatorios.map(rec => [
      rec.nombre_medicamento,
      rec.dosis,
      rec.frecuencia,
      rec.horarios.join(', '),
      format(new Date(rec.fecha_inicio), 'PP', { locale: es }),
      rec.fecha_fin ? format(new Date(rec.fecha_fin), 'PP', { locale: es }) : 'Indefinido',
      rec.activo ? 'Activo' : 'Inactivo',
    ]);

    autoTable(doc, {
      head: [['Medicamento', 'Dosis', 'Frecuencia', 'Horarios', 'Inicio', 'Fin', 'Estado']],
      body: tableData,
      startY: 40,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [59, 130, 246] },
    });
  };

  const generarPDF = async () => {
    setExportando(true);
    try {
      const doc = new jsPDF();
      
      // Encabezado
      doc.setFontSize(18);
      doc.setTextColor(59, 130, 246);
      doc.text(titulo, 105, 20, { align: 'center' });
      
      // Información
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.text(`Generado: ${format(new Date(), 'PPP', { locale: es })}`, 20, 30);
      doc.text(`Total de registros: ${datos.length}`, 20, 35);
      
      // Tabla según tipo
      if (tipo === 'citas') {
        exportarCitas(doc, datos as CitaPaciente[]);
      } else if (tipo === 'estudios') {
        exportarEstudios(doc, datos as SolicitudEstudio[]);
      } else if (tipo === 'recordatorios') {
        exportarRecordatorios(doc, datos as RecordatorioMedicamento[]);
      }
      
      // Pie de página
      const pageCount = doc.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.text(
          `Página ${i} de ${pageCount} - Sistema DDX Medical`,
          105,
          285,
          { align: 'center' }
        );
      }
      
      // Descargar
      const nombreArchivo = `${tipo}-${format(new Date(), 'yyyy-MM-dd')}.pdf`;
      doc.save(nombreArchivo);
    } catch (error) {
      console.error('Error al exportar PDF:', error);
    } finally {
      setExportando(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={generarPDF}
      disabled={exportando || datos.length === 0}
      className="gap-2"
    >
      {exportando ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <FileDown className="h-4 w-4" />
      )}
      Exportar a PDF
    </Button>
  );
}
