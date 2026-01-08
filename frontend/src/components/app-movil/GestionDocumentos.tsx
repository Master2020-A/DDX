import { useState, useEffect } from 'react';
import { FileText, Download, Eye, CheckCircle, Clock } from 'lucide-react';
import appMovilService, { DocumentoEscaneado, TipoDocumento } from '../../services/appMovilService';

const GestionDocumentos = () => {
  const [documentos, setDocumentos] = useState<DocumentoEscaneado[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroTipo, setFiltroTipo] = useState<TipoDocumento | ''>('');

  useEffect(() => {
    cargarDocumentos();
  }, [filtroTipo]);

  const cargarDocumentos = async () => {
    try {
      setLoading(true);
      const params: any = { limite: 50 };
      if (filtroTipo) params.tipo = filtroTipo;
      
      const data = await appMovilService.listarDocumentos(params);
      setDocumentos(data);
    } catch (error) {
      console.error('Error al cargar documentos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Documentos Escaneados
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Documentos capturados desde la aplicación móvil
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Filtrar por tipo:
          </label>
          <select
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value as TipoDocumento | '')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-50"
          >
            <option value="">Todos</option>
            <option value={TipoDocumento.IDENTIFICACION}>Identificación</option>
            <option value={TipoDocumento.RECETA}>Receta</option>
            <option value={TipoDocumento.LABORATORIO}>Laboratorio</option>
            <option value={TipoDocumento.ESTUDIO}>Estudio</option>
            <option value={TipoDocumento.CONSENTIMIENTO}>Consentimiento</option>
            <option value={TipoDocumento.OTRO}>Otro</option>
          </select>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Documentos</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                {documentos.length}
              </p>
            </div>
            <FileText className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Con OCR</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
                {documentos.filter(d => d.ocr_procesado).length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Firmados</p>
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">
                {documentos.filter(d => d.firmado).length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Sincronizados</p>
              <p className="text-2xl font-bold text-cyan-600 dark:text-cyan-400 mt-1">
                {documentos.filter(d => d.sincronizado).length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-cyan-500" />
          </div>
        </div>
      </div>

      {/* Lista de Documentos */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
            Lista de Documentos
          </h3>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {documentos.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-50">
                No hay documentos
              </h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Los documentos escaneados desde la app aparecerán aquí
              </p>
            </div>
          ) : (
            documentos.map((documento) => (
              <div key={documento.id} className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <span className="text-3xl">
                      {appMovilService.obtenerIconoTipoDocumento(documento.tipo)}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                          {documento.nombre}
                        </p>
                        {documento.firmado && (
                          <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 rounded-full">
                            Firmado
                          </span>
                        )}
                        {documento.ocr_procesado && (
                          <span className="px-2 py-0.5 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                            OCR
                          </span>
                        )}
                        {documento.sincronizado && (
                          <span className="px-2 py-0.5 text-xs bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200 rounded-full">
                            Sincronizado
                          </span>
                        )}
                      </div>
                      {documento.descripcion && (
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                          {documento.descripcion}
                        </p>
                      )}
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                        <span className="capitalize">{documento.tipo}</span>
                        {documento.tamano_bytes && (
                          <span>{appMovilService.formatearTamano(documento.tamano_bytes)}</span>
                        )}
                        <span>
                          {appMovilService.calcularTiempoTranscurrido(documento.created_at)}
                        </span>
                        {documento.confianza_ocr && (
                          <span>Confianza OCR: {documento.confianza_ocr}%</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50"
                      title="Ver documento"
                    >
                      <Eye className="h-5 w-5" />
                    </button>
                    <button
                      className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50"
                      title="Descargar"
                    >
                      <Download className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default GestionDocumentos;
