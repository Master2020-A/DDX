import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { FHIRObservation } from '@/types/fhirObservation';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { TrendingUp } from 'lucide-react';

interface ObservationTrendsProps {
  observations: FHIRObservation[];
}

interface TrendData {
  date: string;
  value: number;
  interpretation?: string;
  referenceHigh?: number;
  referenceLow?: number;
}

export const ObservationTrends: React.FC<ObservationTrendsProps> = ({ observations }) => {
  const [selectedCode, setSelectedCode] = useState<string>('');
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [availableCodes, setAvailableCodes] = useState<Array<{ code: string; display: string }>>([]);

  useEffect(() => {
    // Extraer códigos únicos de las observaciones
    const codes = new Map<string, string>();
    
    observations.forEach(obs => {
      if (obs.code.coding && obs.code.coding.length > 0) {
        const coding = obs.code.coding[0];
        codes.set(coding.code, obs.code.text || coding.display || coding.code);
      }
    });

    const codesList = Array.from(codes.entries()).map(([code, display]) => ({
      code,
      display
    }));

    setAvailableCodes(codesList);

    // Seleccionar el primer código por defecto
    if (codesList.length > 0 && !selectedCode) {
      setSelectedCode(codesList[0].code);
    }
  }, [observations]);

  useEffect(() => {
    if (!selectedCode) return;

    // Filtrar observaciones por código seleccionado
    const filteredObs = observations.filter(obs => 
      obs.code.coding?.some(c => c.code === selectedCode)
    );

    // Convertir a datos de tendencia
    const data: TrendData[] = filteredObs
      .filter(obs => obs.value_quantity && obs.effective_datetime)
      .map(obs => {
        const interpretationCode = obs.interpretation?.[0]?.coding?.[0]?.code;
        const refRange = obs.reference_range?.[0];

        return {
          date: format(new Date(obs.effective_datetime!), 'dd/MM HH:mm', { locale: es }),
          value: obs.value_quantity!.value,
          interpretation: interpretationCode,
          referenceHigh: refRange?.high?.value,
          referenceLow: refRange?.low?.value
        };
      })
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    setTrendData(data);
  }, [selectedCode, observations]);

  const getPointColor = (interpretation?: string) => {
    switch (interpretation) {
      case 'N': return '#10b981'; // green
      case 'L': return '#3b82f6'; // blue
      case 'H': return '#f97316'; // orange
      case 'LL':
      case 'HH':
      case 'AA': return '#ef4444'; // red
      default: return '#6b7280'; // gray
    }
  };

  if (availableCodes.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-gray-600">No hay datos suficientes para mostrar tendencias</p>
        </CardContent>
      </Card>
    );
  }

  const hasReferenceRange = trendData.some(d => d.referenceHigh !== undefined || d.referenceLow !== undefined);
  const referenceHigh = trendData.find(d => d.referenceHigh)?.referenceHigh;
  const referenceLow = trendData.find(d => d.referenceLow)?.referenceLow;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Tendencias Temporales
          </CardTitle>
          <div className="w-64">
            <Select value={selectedCode} onValueChange={setSelectedCode}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar parámetro" />
              </SelectTrigger>
              <SelectContent>
                {availableCodes.map(({ code, display }) => (
                  <SelectItem key={code} value={code}>
                    {display}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {trendData.length === 0 ? (
          <div className="text-center py-8 text-gray-600">
            No hay datos para este parámetro
          </div>
        ) : (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '12px'
                  }}
                  formatter={(value: number) => [value.toFixed(2), 'Valor']}
                />
                <Legend />
                
                {/* Líneas de referencia */}
                {hasReferenceRange && referenceHigh && (
                  <ReferenceLine 
                    y={referenceHigh} 
                    stroke="#f97316" 
                    strokeDasharray="3 3"
                    label={{ value: 'Máx', position: 'right', fill: '#f97316', fontSize: 12 }}
                  />
                )}
                {hasReferenceRange && referenceLow && (
                  <ReferenceLine 
                    y={referenceLow} 
                    stroke="#3b82f6" 
                    strokeDasharray="3 3"
                    label={{ value: 'Mín', position: 'right', fill: '#3b82f6', fontSize: 12 }}
                  />
                )}
                
                {/* Línea de valores */}
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  dot={(props: any) => {
                    const { cx, cy, payload } = props;
                    return (
                      <circle
                        cx={cx}
                        cy={cy}
                        r={5}
                        fill={getPointColor(payload.interpretation)}
                        stroke="white"
                        strokeWidth={2}
                      />
                    );
                  }}
                  activeDot={{ r: 8 }}
                  name="Valor"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Leyenda de colores */}
        <div className="mt-4 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Normal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>Bajo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span>Alto</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span>Crítico</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
