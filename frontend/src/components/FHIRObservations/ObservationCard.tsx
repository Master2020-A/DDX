import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Activity, 
  Beaker, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { 
  FHIRObservation, 
  OBSERVATION_STATUS_LABELS,
  OBSERVATION_CATEGORY_LABELS,
  INTERPRETATION_CODES
} from '@/types/fhirObservation';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface ObservationCardProps {
  observation: FHIRObservation;
  onClick?: () => void;
}

export const ObservationCard: React.FC<ObservationCardProps> = ({ observation, onClick }) => {
  // Obtener el valor principal
  const getValue = () => {
    if (observation.value_quantity) {
      return `${observation.value_quantity.value} ${observation.value_quantity.unit || ''}`;
    }
    if (observation.value_string) return observation.value_string;
    if (observation.value_boolean !== undefined) return observation.value_boolean ? 'Sí' : 'No';
    if (observation.value_integer !== undefined) return observation.value_integer.toString();
    if (observation.component && observation.component.length > 0) {
      return `${observation.component.length} componentes`;
    }
    return 'N/A';
  };

  // Obtener interpretación
  const getInterpretation = () => {
    if (!observation.interpretation || observation.interpretation.length === 0) {
      return null;
    }
    
    const code = observation.interpretation[0].coding?.[0]?.code || 'N';
    const interpretation = INTERPRETATION_CODES[code] || { label: 'Desconocido', color: 'gray' };
    
    return interpretation;
  };

  // Obtener icono según categoría
  const getCategoryIcon = () => {
    const category = observation.category[0];
    switch (category) {
      case 'vital-signs':
        return <Activity className="h-5 w-5" />;
      case 'laboratory':
        return <Beaker className="h-5 w-5" />;
      default:
        return <Activity className="h-5 w-5" />;
    }
  };

  // Obtener icono de tendencia según interpretación
  const getInterpretationIcon = () => {
    const interpretation = getInterpretation();
    if (!interpretation) return <Minus className="h-4 w-4" />;
    
    switch (interpretation.color) {
      case 'green':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'blue':
        return <TrendingDown className="h-4 w-4 text-blue-600" />;
      case 'orange':
        return <TrendingUp className="h-4 w-4 text-orange-600" />;
      case 'red':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4" />;
    }
  };

  const interpretation = getInterpretation();
  const categoryLabel = OBSERVATION_CATEGORY_LABELS[observation.category[0]] || observation.category[0];
  const statusLabel = OBSERVATION_STATUS_LABELS[observation.status] || observation.status;

  return (
    <Card 
      className={`cursor-pointer hover:shadow-md transition-shadow ${
        interpretation?.color === 'red' ? 'border-red-300' : ''
      }`}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getCategoryIcon()}
            <CardTitle className="text-base">
              {observation.code.text || observation.code.coding?.[0]?.display || 'Observación'}
            </CardTitle>
          </div>
          <Badge variant={observation.status === 'final' ? 'default' : 'secondary'}>
            {statusLabel}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {/* Valor principal */}
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-gray-900">
              {getValue()}
            </span>
            {getInterpretationIcon()}
          </div>

          {/* Interpretación */}
          {interpretation && (
            <div className="flex items-center gap-2">
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
            </div>
          )}

          {/* Rango de referencia */}
          {observation.reference_range && observation.reference_range.length > 0 && (
            <div className="text-sm text-gray-600">
              Rango: {observation.reference_range[0].low?.value || '—'} - {observation.reference_range[0].high?.value || '—'} {observation.reference_range[0].low?.unit || ''}
            </div>
          )}

          {/* Metadatos */}
          <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t">
            <span className="flex items-center gap-1">
              <Badge variant="outline" className="text-xs">
                {categoryLabel}
              </Badge>
            </span>
            <span>
              {observation.effective_datetime && 
                format(new Date(observation.effective_datetime), "dd MMM yyyy HH:mm", { locale: es })
              }
            </span>
          </div>

          {/* Código LOINC */}
          {observation.code.coding && observation.code.coding.length > 0 && (
            <div className="text-xs text-gray-400">
              LOINC: {observation.code.coding[0].code}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
