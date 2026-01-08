import { Button } from '@/components/ui/button';
import { Download, FileText, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { PagoServicio } from '@/services/portalPacienteService';
import jsPDF from 'jspdf';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface DescargaComprobanteProps {
  pago: PagoServicio;
}

export default function DescargaComprobante({ pago }: DescargaComprobanteProps) {
  const [descargando, setDescargando] = useState(false);

  const generarPDF = async () => {
    setDescargando(true);
    try {
      const doc = new jsPDF();
      
      // Encabezado
      doc.setFontSize(20);
      doc.setTextColor(59, 130, 246); // Azul
      doc.text('COMPROBANTE DE PAGO', 105, 20, { align: 'center' });
      
      // Línea separadora
      doc.setDrawColor(200, 200, 200);
      doc.line(20, 25, 190, 25);
      
      // Información del sistema
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.text('Sistema DDX Medical', 20, 35);
      doc.text(`Fecha de emisión: ${format(new Date(), 'PPP', { locale: es })}`, 20, 40);
      
      // Información del pago
      doc.setFontSize(12);
      doc.setTextColor(0, 0, 0);
      doc.text('DATOS DEL PAGO', 20, 55);
      
      doc.setFontSize(10);
      const yStart = 65;
      const lineHeight = 7;
      
      doc.text(`Referencia: ${pago.referencia_pago || 'N/A'}`, 20, yStart);
      doc.text(`Concepto: ${pago.concepto}`, 20, yStart + lineHeight);
      if (pago.descripcion) {
        doc.text(`Descripción: ${pago.descripcion}`, 20, yStart + lineHeight * 2);
      }
      
      doc.text(`Monto: $${pago.monto.toFixed(2)} ${pago.moneda}`, 20, yStart + lineHeight * 3);
      doc.text(`Método de Pago: ${pago.metodo_pago.replace('_', ' ').toUpperCase()}`, 20, yStart + lineHeight * 4);
      doc.text(`Estado: ${pago.estado.toUpperCase()}`, 20, yStart + lineHeight * 5);
      
      if (pago.fecha_pago) {
        doc.text(
          `Fecha de Pago: ${format(new Date(pago.fecha_pago), 'PPP', { locale: es })}`,
          20,
          yStart + lineHeight * 6
        );
      }
      
      if (pago.fecha_completado) {
        doc.text(
          `Fecha de Completado: ${format(new Date(pago.fecha_completado), 'PPP', { locale: es })}`,
          20,
          yStart + lineHeight * 7
        );
      }
      
      // Cuadro de monto destacado
      doc.setFillColor(240, 240, 240);
      doc.rect(20, yStart + lineHeight * 9, 170, 20, 'F');
      doc.setFontSize(14);
      doc.setTextColor(0, 0, 0);
      doc.text('MONTO TOTAL:', 25, yStart + lineHeight * 10);
      doc.setFontSize(16);
      doc.setTextColor(59, 130, 246);
      doc.text(`$${pago.monto.toFixed(2)} ${pago.moneda}`, 160, yStart + lineHeight * 10, { align: 'right' });
      
      // Información adicional
      if (pago.datos_transaccion) {
        doc.setFontSize(10);
        doc.setTextColor(0, 0, 0);
        doc.text('DATOS DE TRANSACCIÓN', 20, yStart + lineHeight * 12);
        doc.setFontSize(8);
        doc.setTextColor(100, 100, 100);
        const transaccionStr = JSON.stringify(pago.datos_transaccion, null, 2);
        const lines = doc.splitTextToSize(transaccionStr, 170);
        doc.text(lines, 20, yStart + lineHeight * 13);
      }
      
      // Pie de página
      doc.setFontSize(8);
      doc.setTextColor(150, 150, 150);
      doc.text('Este es un comprobante electrónico generado por el Sistema DDX Medical', 105, 280, { align: 'center' });
      doc.text(`ID de Pago: ${pago.id}`, 105, 285, { align: 'center' });
      
      // Descargar
      doc.save(`comprobante-pago-${pago.referencia_pago || pago.id}.pdf`);
    } catch (error) {
      console.error('Error al generar PDF:', error);
    } finally {
      setDescargando(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={generarPDF}
      disabled={descargando}
      className="gap-2"
    >
      {descargando ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Download className="h-4 w-4" />
      )}
      Descargar Comprobante
    </Button>
  );
}
