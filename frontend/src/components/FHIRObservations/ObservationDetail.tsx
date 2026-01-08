import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  FHIRObservation, 
  OBSERVATION_STATUS_LABELS,
  OBSERVATION_CATEGORY_LABELS,
  INTERPRETATION_CODES,
  LOINC_COMMON_CODES
} from '@/types/fhirObservation';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { 
  Activity, 
  Calendar, 
  FileText, 
  AlertCircle,
  CheckCircle,
  Info
} from 'lucide-react';

interface ObservationDetailProps {
  observation: FHIRObservation;
}

export const ObservationDetail: React.FC<ObservationDetailProps> = ({ observation }) => {
  const getInterpretationBadge = (code: string) => {
    const interpretation = INTERPRETATION_CODES[code] || { label: code, color: 'gray' };
    
    return (
      <Badge 
        variant="outline"
        className={`
          ${interpretation.color === 'green' ? 'bg-green-50 text-green-700 border-green-200' : ''}
          ${interpretation.color === 'blue' ? 'bg-blue-50 text-blue-700 border-blue-200' : ''}
          ${interpretation.color === 'orange' ? 'bg-orange-50 text-orange-700 border-orange-200' : ''}
          ${interpretation.color === 'red' ? 'bg-red-50 text-red-700 border-red-200' : ''}
          ${interpretation.color === 'yellow' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' : ''}
        `}
      >
        {interpretation.label}
      </Badge>
    );
  };

  const renderValue = () => {
    if (observation.value_quantity) {
      return (
        <div className="text-3xl font-bold text-gray-900">
          {observation.value_quantity.value} {observation.value_quantity.unit || ''}
        </div>
      );
    }
    if (observation.value_string) {
      return <div className="text-xl text-gray-900">{observation.value_string}</div>;
    }
    if (observation.value_boolean !== undefined) {
      return <div className="text-xl text-gray-900">{observation.value_boolean ? 'Sí' : 'No'}</div>;
    }
    if (observation.value_integer !== undefined) {
      return <div className="text-3xl font-bold text-gray-900">{observation.value_integer}</div>;
    }
    return null;
  };

  const categoryLabel = OBSERVATION_CATEGORY_LABELS[observation.category[0]] || observation.category[0];
  const statusLabel = OBSERVATION_STATUS_LABELS[observation.status] || observation.status;

  return (
    <div className="space-y-6">
      {/* Encabezado */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">
                {observation.code.text || observation.code.coding?.[0]?.display || 'Observación FHIR'}
              </CardTitle>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant="outline">{categoryLabel}</Badge>
                <Badge variant={observation.status === 'final' ? 'default' : 'secondary'}>
                  {statusLabel}
                </Badge>
              </div>
            </div>
            {observation.interpretation && observation.interpretation.length > 0 && (
              <div>
                {getInterpretationBadge(observation.interpretation[0].coding?.[0]?.code || 'N')}
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Valor principal */}
            {renderValue()}

            {/* Código LOINC */}
            {observation.code.coding && observation.code.coding.length > 0 && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Info className="h-4 w-4" />
                <span>
                  Código LOINC: <strong>{observation.code.coding[0].code}</strong>
                  {LOINC_COMMON_CODES[observation.code.coding[0].code] && 
                    ` - ${LOINC_COMMON_CODES[observation.code.coding[0].code]}`
                  }
                </span>
              </div>
            )}

            {/* Fecha */}
            {observation.effective_datetime && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Calendar className="h-4 w-4" />
                <span>
                  {format(new Date(observation.effective_datetime), "dd 'de' MMMM 'de' yyyy 'a las' HH:mm", { locale: es })}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Rango de Referencia */}
      {observation.reference_range && observation.reference_range.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Rango de Referencia</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {observation.reference_range.map((range, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="text-sm text-gray-600">Rango Normal</div>
                    <div className="font-semibold">
                      {range.low?.value || '—'} - {range.high?.value || '—'} {range.low?.unit || ''}
                    </div>
                  </div>
                  {observation.value_quantity && range.low && range.high && (
                    <div>
                      {observation.value_quantity.value < range.low.value ? (
                        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                          Por debajo
                        </Badge>
                      ) : observation.value_quantity.value > range.high.value ? (
                        <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                          Por encima
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                          Dentro del rango
                        </Badge>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Componentes (para observaciones multi-valor como presión arterial) */}
      {observation.component && observation.component.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Componentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {observation.component.map((comp, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">
                        {comp.code.text || comp.code.coding?.[0]?.display || `Componente ${index + 1}`}
                      </div>
                      {comp.code.coding && comp.code.coding.length > 0 && (
                        <div className="text-xs text-gray-500">
                          LOINC: {comp.code.coding[0].code}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      {comp.valueQuantity && (
                        <div className="text-2xl font-bold">
                          {comp.valueQuantity.value} {comp.valueQuantity.unit || ''}
                        </div>
                      )}
                      {comp.interpretation && comp.interpretation.length > 0 && (
                        <div className="mt-1">
                          {getInterpretationBadge(comp.interpretation[0].coding?.[0]?.code || 'N')}
                        </div>
                      )}
                    </div>
                  </div>
                  {comp.referenceRange && comp.referenceRange.length > 0 && (
                    <div className="mt-2 text-sm text-gray-600">
                      Rango: {comp.referenceRange[0].low?.value || '—'} - {comp.referenceRange[0].high?.value || '—'} {comp.referenceRange[0].low?.unit || ''}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Notas */}
      {observation.note && observation.note.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Notas e Interpretación
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {observation.note.map((note, index) => (
                <div key={index} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-gray-800 whitespace-pre-wrap">{note.text}</p>
                  {note.time && (
                    <p className="text-xs text-gray-500 mt-2">
                      {format(new Date(note.time), "dd/MM/yyyy HH:mm", { locale: es })}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Metadatos */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Información Adicional</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-600">ID de Observación</div>
              <div className="font-mono text-xs">{observation.id}</div>
            </div>
            {observation.source_type && (
              <div>
                <div className="text-gray-600">Origen</div>
                <div className="font-semibold capitalize">{observation.source_type}</div>
              </div>
            )}
            <div>
              <div className="text-gray-600">Creado</div>
              <div>{format(new Date(observation.created_at), "dd/MM/yyyy HH:mm", { locale: es })}</div>
            </div>
            <div>
              <div className="text-gray-600">Actualizado</div>
              <div>{format(new Date(observation.updated_at), "dd/MM/yyyy HH:mm", { locale: es })}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
