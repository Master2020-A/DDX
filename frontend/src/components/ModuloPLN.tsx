/**
 * Componente de ejemplo para usar el Módulo de Procesamiento de Lenguaje Natural (PLN)
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Mic, FileText, FileSearch, Languages, Loader2 } from 'lucide-react';
import api from '@/services/api';

interface ModuloPLNProps {
  pacienteId: string;
}

export default function ModuloPLN({ pacienteId }: ModuloPLNProps) {
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState<any>(null);

  // ==================== TRANSCRIPCIÓN ====================
  const [archivoAudio, setArchivoAudio] = useState<File | null>(null);

  const transcribirAudio = async () => {
    if (!archivoAudio) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('archivo', archivoAudio);
      formData.append('paciente_id', pacienteId);
      formData.append('idioma', 'es');
      formData.append('extraer_informacion', 'true');

      const response = await api.post('/pln/transcribir-audio', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResultado(response.data);
    } catch (error) {
      console.error('Error transcribiendo audio:', error);
      alert('Error al transcribir audio');
    } finally {
      setLoading(false);
    }
  };

  // ==================== EXTRACCIÓN ====================
  const [textoExtraer, setTextoExtraer] = useState('');

  const extraerInformacion = async () => {
    if (!textoExtraer.trim()) return;

    setLoading(true);
    try {
      const response = await api.post('/pln/extraer-informacion', {
        texto: textoExtraer,
        tipo_documento: 'nota_evolucion',
        paciente_id: pacienteId
      });

      setResultado(response.data);
    } catch (error) {
      console.error('Error extrayendo información:', error);
      alert('Error al extraer información');
    } finally {
      setLoading(false);
    }
  };

  // ==================== RESUMEN ====================
  const [periodoDias, setPeriodoDias] = useState('90');

  const generarResumen = async () => {
    setLoading(true);
    try {
      const response = await api.post('/pln/generar-resumen', {
        paciente_id: pacienteId,
        tipo_resumen: 'completo',
        periodo_dias: parseInt(periodoDias),
        incluir_consultas: true,
        incluir_laboratorios: true,
        incluir_imagenes: true,
        incluir_medicamentos: true
      });

      setResultado(response.data);
    } catch (error) {
      console.error('Error generando resumen:', error);
      alert('Error al generar resumen');
    } finally {
      setLoading(false);
    }
  };

  // ==================== TRADUCCIÓN ====================
  const [textoTraducir, setTextoTraducir] = useState('');
  const [idiomaDestino, setIdiomaDestino] = useState('en');

  const traducirTexto = async () => {
    if (!textoTraducir.trim()) return;

    setLoading(true);
    try {
      const response = await api.post('/pln/traducir', {
        texto: textoTraducir,
        idioma_origen: 'es',
        idioma_destino: idiomaDestino,
        tipo_contenido: 'termino_medico'
      });

      setResultado(response.data);
    } catch (error) {
      console.error('Error traduciendo:', error);
      alert('Error al traducir');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>🧠 Procesamiento de Lenguaje Natural (PLN)</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="transcripcion">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="transcripcion">
                <Mic className="w-4 h-4 mr-2" />
                Transcripción
              </TabsTrigger>
              <TabsTrigger value="extraccion">
                <FileSearch className="w-4 h-4 mr-2" />
                Extracción
              </TabsTrigger>
              <TabsTrigger value="resumen">
                <FileText className="w-4 h-4 mr-2" />
                Resumen
              </TabsTrigger>
              <TabsTrigger value="traduccion">
                <Languages className="w-4 h-4 mr-2" />
                Traducción
              </TabsTrigger>
            </TabsList>

            {/* ==================== TAB: TRANSCRIPCIÓN ==================== */}
            <TabsContent value="transcripcion" className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Subir archivo de audio
                </label>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setArchivoAudio(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Formatos soportados: MP3, WAV, M4A, OGG, FLAC
                </p>
              </div>

              <Button
                onClick={transcribirAudio}
                disabled={!archivoAudio || loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Transcribiendo...
                  </>
                ) : (
                  <>
                    <Mic className="w-4 h-4 mr-2" />
                    Transcribir Audio
                  </>
                )}
              </Button>

              {resultado?.texto && (
                <div className="mt-4 p-4 bg-gray-50 rounded-md">
                  <h4 className="font-semibold mb-2">Texto transcrito:</h4>
                  <p className="text-sm">{resultado.texto}</p>

                  {resultado.informacion_extraida && (
                    <div className="mt-4">
                      <h4 className="font-semibold mb-2">Información extraída:</h4>
                      <pre className="text-xs bg-white p-2 rounded overflow-auto max-h-60">
                        {JSON.stringify(resultado.informacion_extraida, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </TabsContent>

            {/* ==================== TAB: EXTRACCIÓN ==================== */}
            <TabsContent value="extraccion" className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Texto médico a analizar
                </label>
                <Textarea
                  value={textoExtraer}
                  onChange={(e) => setTextoExtraer(e.target.value)}
                  placeholder="Ej: Paciente masculino de 45 años con cefalea intensa de 3 días de evolución..."
                  rows={6}
                />
              </div>

              <Button
                onClick={extraerInformacion}
                disabled={!textoExtraer.trim() || loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Extrayendo...
                  </>
                ) : (
                  <>
                    <FileSearch className="w-4 h-4 mr-2" />
                    Extraer Información
                  </>
                )}
              </Button>

              {resultado?.sintomas && (
                <div className="mt-4 space-y-4">
                  {resultado.sintomas.length > 0 && (
                    <div className="p-4 bg-red-50 rounded-md">
                      <h4 className="font-semibold mb-2">Síntomas:</h4>
                      <ul className="list-disc list-inside text-sm">
                        {resultado.sintomas.map((s: any, i: number) => (
                          <li key={i}>
                            {s.nombre} - {s.intensidad} ({s.duracion})
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {resultado.medicamentos?.length > 0 && (
                    <div className="p-4 bg-green-50 rounded-md">
                      <h4 className="font-semibold mb-2">Medicamentos:</h4>
                      <ul className="list-disc list-inside text-sm">
                        {resultado.medicamentos.map((m: any, i: number) => (
                          <li key={i}>
                            {m.nombre_generico} {m.dosis} - {m.frecuencia}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {resultado.signos_vitales && (
                    <div className="p-4 bg-blue-50 rounded-md">
                      <h4 className="font-semibold mb-2">Signos vitales:</h4>
                      <pre className="text-xs">
                        {JSON.stringify(resultado.signos_vitales, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </TabsContent>

            {/* ==================== TAB: RESUMEN ==================== */}
            <TabsContent value="resumen" className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Período a resumir
                </label>
                <Select value={periodoDias} onValueChange={setPeriodoDias}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30">Últimos 30 días</SelectItem>
                    <SelectItem value="90">Últimos 90 días</SelectItem>
                    <SelectItem value="180">Últimos 6 meses</SelectItem>
                    <SelectItem value="365">Último año</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={generarResumen}
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generando resumen...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Generar Resumen Clínico
                  </>
                )}
              </Button>

              {resultado?.resumen_texto && (
                <div className="mt-4 space-y-4">
                  <div className="p-4 bg-gray-50 rounded-md">
                    <h4 className="font-semibold mb-2">Resumen:</h4>
                    <p className="text-sm whitespace-pre-wrap">{resultado.resumen_texto}</p>
                  </div>

                  {resultado.diagnosticos_actuales?.length > 0 && (
                    <div className="p-4 bg-yellow-50 rounded-md">
                      <h4 className="font-semibold mb-2">Diagnósticos actuales:</h4>
                      <ul className="list-disc list-inside text-sm">
                        {resultado.diagnosticos_actuales.map((d: string, i: number) => (
                          <li key={i}>{d}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {resultado.tratamiento_actual?.length > 0 && (
                    <div className="p-4 bg-green-50 rounded-md">
                      <h4 className="font-semibold mb-2">Tratamiento actual:</h4>
                      <ul className="list-disc list-inside text-sm">
                        {resultado.tratamiento_actual.map((t: string, i: number) => (
                          <li key={i}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </TabsContent>

            {/* ==================== TAB: TRADUCCIÓN ==================== */}
            <TabsContent value="traduccion" className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Término o texto a traducir
                </label>
                <Textarea
                  value={textoTraducir}
                  onChange={(e) => setTextoTraducir(e.target.value)}
                  placeholder="Ej: Hipertensión arterial esencial"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Idioma destino
                </label>
                <Select value={idiomaDestino} onValueChange={setIdiomaDestino}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">🇬🇧 Inglés</SelectItem>
                    <SelectItem value="fr">🇫🇷 Francés</SelectItem>
                    <SelectItem value="pt">🇵🇹 Portugués</SelectItem>
                    <SelectItem value="de">🇩🇪 Alemán</SelectItem>
                    <SelectItem value="it">🇮🇹 Italiano</SelectItem>
                    <SelectItem value="la">🏛️ Latín</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={traducirTexto}
                disabled={!textoTraducir.trim() || loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Traduciendo...
                  </>
                ) : (
                  <>
                    <Languages className="w-4 h-4 mr-2" />
                    Traducir
                  </>
                )}
              </Button>

              {resultado?.texto_traducido && (
                <div className="mt-4 space-y-4">
                  <div className="p-4 bg-blue-50 rounded-md">
                    <h4 className="font-semibold mb-2">Traducción:</h4>
                    <p className="text-lg">{resultado.texto_traducido}</p>
                  </div>

                  {resultado.alternativas?.length > 0 && (
                    <div className="p-4 bg-gray-50 rounded-md">
                      <h4 className="font-semibold mb-2">Alternativas:</h4>
                      <ul className="list-disc list-inside text-sm">
                        {resultado.alternativas.map((a: string, i: number) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {resultado.definicion && (
                    <div className="p-4 bg-green-50 rounded-md">
                      <h4 className="font-semibold mb-2">Definición:</h4>
                      <p className="text-sm">{resultado.definicion}</p>
                    </div>
                  )}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
