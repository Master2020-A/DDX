import React from 'react';
import { Filter, X } from 'lucide-react';

interface FilterBarProps {
  filters: {
    estado?: string;
    urgencia?: string;
    especialidad?: string;
  };
  onFilterChange: (filters: any) => void;
  onClearFilters: () => void;
}

const ESTADOS = [
  { value: '', label: 'Todos' },
  { value: 'solicitada', label: 'Solicitada' },
  { value: 'aceptada', label: 'Aceptada' },
  { value: 'completada', label: 'Completada' },
  { value: 'rechazada', label: 'Rechazada' },
];

const URGENCIAS = [
  { value: '', label: 'Todas' },
  { value: 'normal', label: 'Normal' },
  { value: 'urgente', label: 'Urgente' },
  { value: 'emergencia', label: 'Emergencia' },
];

const ESPECIALIDADES = [
  { value: '', label: 'Todas' },
  { value: 'Cardiología', label: 'Cardiología' },
  { value: 'Neurología', label: 'Neurología' },
  { value: 'Pediatría', label: 'Pediatría' },
  { value: 'Traumatología', label: 'Traumatología' },
  { value: 'Psiquiatría', label: 'Psiquiatría' },
];

export default function FilterBar({ filters, onFilterChange, onClearFilters }: FilterBarProps) {
  const hasActiveFilters = filters.estado || filters.urgencia || filters.especialidad;

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-4">
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
          <Filter size={18} />
          <span className="font-medium">Filtros:</span>
        </div>

        <select
          value={filters.estado || ''}
          onChange={(e) => onFilterChange({ ...filters, estado: e.target.value || undefined })}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {ESTADOS.map(e => (
            <option key={e.value} value={e.value}>{e.label}</option>
          ))}
        </select>

        <select
          value={filters.urgencia || ''}
          onChange={(e) => onFilterChange({ ...filters, urgencia: e.target.value || undefined })}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {URGENCIAS.map(u => (
            <option key={u.value} value={u.value}>{u.label}</option>
          ))}
        </select>

        <select
          value={filters.especialidad || ''}
          onChange={(e) => onFilterChange({ ...filters, especialidad: e.target.value || undefined })}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {ESPECIALIDADES.map(esp => (
            <option key={esp.value} value={esp.value}>{esp.label}</option>
          ))}
        </select>

        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
          >
            <X size={16} />
            Limpiar filtros
          </button>
        )}
      </div>
    </div>
  );
}