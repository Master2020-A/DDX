import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Heart, TrendingUp } from 'lucide-react';

interface InterpretacionNarrativa {
  P: string;
  PR: string;
  QRS: string;
  ST_T: string;
  QT: string;
}

interface VisualizadorOndasEKGProps {
  interpretacion: InterpretacionNarrativa;
  diagnostico?: string;
  riesgo?: string;
  hallazgos?: Array<{
    condition: string;
    severity: string;
    description: string;
  }>;
}

const VisualizadorOndasEKG: React.FC<VisualizadorOndasEKGProps> = ({
  interpretacion,
  diagnostico,
  riesgo,
  hallazgos = []
}) => {
  const getRiesgoColor = (riesgo?: string) => {
    if (!riesgo) return 'bg-gray-100 text-gray-800';
    if (riesgo.includes('NORMAL') || riesgo.includes('BAJO')) return 'bg-green-100 text-green-800';
    if (riesgo.includes('INTERMEDIO')) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-blue-100 text-blue-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      {/* Encabezado con diagnóstico y riesgo */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Heart className="h-5 w-5 text-red-500" />
          <h3 className="text-lg font-semibold">Interpretación Narrativa Detallada</h3>
        </div>
        {riesgo && (
          <Badge className={getRiesgoColor(riesgo)}>
            {riesgo}
          </Badge>
        )}
      </div>

      {/* Diagnóstico principal */}
      {diagnostico && (
        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-500" />
              <span className="font-semibold">Diagnóstico del Ritmo:</span>
              <span>{diagnostico}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Interpretación por componentes */}
      <div className="grid gap-4">
        {/* Onda P */}
        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              A. Onda P (Actividad Auricular)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">{interpretacion.P}</p>
          </CardContent>
        </Card>

        {/* Intervalo PR */}
        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-500"></span>
              B. Intervalo PR (Conducción Auriculoventricular)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">{interpretacion.PR}</p>
          </CardContent>
        </Card>

        {/* Complejo QRS */}
        <Card className="border-l-4 border-l-red-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500"></span>
              C. Complejo QRS (Despolarización Ventricular)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">{interpretacion.QRS}</p>
          </CardContent>
        </Card>

        {/* Segmento ST y Onda T */}
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              D. Segmento ST y Onda T (Repolarización)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">{interpretacion.ST_T}</p>
          </CardContent>
        </Card>

        {/* Intervalo QT */}
        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-orange-500"></span>
              E. Intervalo QT
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">{interpretacion.QT}</p>
          </CardContent>
        </Card>
      </div>

      {/* Hallazgos adicionales */}
      {hallazgos.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Hallazgos Clínicos Adicionales
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {hallazgos.map((hallazgo, index) => (
                <div key={index} className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                  <Badge className={getSeverityColor(hallazgo.severity)}>
                    {hallazgo.severity === 'low' ? 'Leve' : 
                     hallazgo.severity === 'moderate' ? 'Moderado' : 'Severo'}
                  </Badge>
                  <div className="flex-1">
                    <p className="font-semibold text-sm">{hallazgo.condition}</p>
                    <p className="text-xs text-gray-600">{hallazgo.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Nota médica */}
      <div className="text-xs text-gray-500 italic border-l-2 border-gray-300 pl-3">
        Interpretación generada mediante análisis avanzado de señales. 
        Requiere validación por médico especialista.
      </div>
    </div>
  );
};

export default VisualizadorOndasEKG;
