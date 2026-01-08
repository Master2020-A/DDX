import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ObservationCard } from './ObservationCard';
import { ObservationDetail } from './ObservationDetail';
import { 
  FHIRObservation, 
  ObservationCategory,
  ObservationStatus,
  OBSERVATION_CATEGORY_LABELS,
  OBSERVATION_STATUS_LABELS
} from '@/types/fhirObservation';
import fhirObservationService from '@/services/fhirObservationService';
import { Filter, RefreshCw, Search } from 'lucide-react';
import { toast } from 'sonner';

interface ObservationListProps {
  patientId: string;
  category?: ObservationCategory;
  showFilters?: boolean;
}

export const ObservationList: React.FC<ObservationListProps> = ({ 
  patientId, 
  category,
  showFilters = true 
}) => {
  const [observations, setObservations] = useState<FHIRObservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedObservation, setSelectedObservation] = useState<FHIRObservation | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  
  // Filtros
  const [filterCategory, setFilterCategory] = useState<ObservationCategory | 'all'>(category || 'all');
  const [filterStatus, setFilterStatus] = useState<ObservationStatus | 'all'>('all');
  const [searchCode, setSearchCode] = useState('');

  useEffect(() => {
    loadObservations();
  }, [patientId, filterCategory, filterStatus]);

  const loadObservations = async () => {
    try {
      setLoading(true);
      const filters: any = {
        patient: patientId,
        limit: 100
      };

      if (filterCategory !== 'all') {
        filters.category = filterCategory;
      }
      if (filterStatus !== 'all') {
        filters.status = filterStatus;
      }
      if (searchCode) {
        filters.code = searchCode;
      }

      const data = await fhirObservationService.listObservations(filters);
      setObservations(data);
    } catch (error) {
      console.error('Error cargando observaciones:', error);
      toast.error('Error al cargar las observaciones');
    } finally {
      setLoading(false);
    }
  };

  const handleObservationClick = (observation: FHIRObservation) => {
    setSelectedObservation(observation);
    setDetailOpen(true);
  };

  const handleRefresh = () => {
    loadObservations();
    toast.success('Observaciones actualizadas');
  };

  const handleSearch = () => {
    loadObservations();
  };

  return (
    <div className="space-y-4">
      {/* Filtros */}
      {showFilters && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filtros
              </CardTitle>
              <Button variant="outline" size="sm" onClick={handleRefresh}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Actualizar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Filtro por categoría */}
              <div>
                <label className="text-sm font-medium mb-2 block">Categoría</label>
                <Select 
                  value={filterCategory} 
                  onValueChange={(value) => setFilterCategory(value as ObservationCategory | 'all')}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Todas las categorías" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las categorías</SelectItem>
                    {Object.entries(OBSERVATION_CATEGORY_LABELS).map(([key, label]) => (
                      <SelectItem key={key} value={key}>{label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Filtro por estado */}
              <div>
                <label className="text-sm font-medium mb-2 block">Estado</label>
                <Select 
                  value={filterStatus} 
                  onValueChange={(value) => setFilterStatus(value as ObservationStatus | 'all')}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Todos los estados" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los estados</SelectItem>
                    {Object.entries(OBSERVATION_STATUS_LABELS).map(([key, label]) => (
                      <SelectItem key={key} value={key}>{label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Búsqueda por código */}
              <div>
                <label className="text-sm font-medium mb-2 block">Código LOINC</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Ej: 8867-4"
                    value={searchCode}
                    onChange={(e) => setSearchCode(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button size="icon" onClick={handleSearch}>
                    <Search className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lista de observaciones */}
      {loading ? (
        <div className="text-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto text-gray-400" />
          <p className="text-gray-600 mt-4">Cargando observaciones...</p>
        </div>
      ) : observations.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-600">No se encontraron observaciones</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {observations.map((observation) => (
            <ObservationCard
              key={observation.id}
              observation={observation}
              onClick={() => handleObservationClick(observation)}
            />
          ))}
        </div>
      )}

      {/* Diálogo de detalle */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Detalle de Observación FHIR</DialogTitle>
          </DialogHeader>
          {selectedObservation && (
            <ObservationDetail observation={selectedObservation} />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};
