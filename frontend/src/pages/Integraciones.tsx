import React, { useState } from 'react';
import {
  Activity,
  FileText,
  Pill,
  DollarSign,
  Settings,
  FileSearch,
} from 'lucide-react';
import DashboardIntegraciones from '../components/integraciones/DashboardIntegraciones';
import RecetaElectronica from '../components/integraciones/RecetaElectronica';
import Farmacia from '../components/integraciones/Farmacia';
import Facturacion from '../components/integraciones/Facturacion';
import Configuracion from '../components/integraciones/Configuracion';
import Logs from '../components/integraciones/Logs';

type TabType = 'dashboard' | 'receta' | 'farmacia' | 'facturacion' | 'configuracion' | 'logs';

const Integraciones: React.FC = () => {
  const [tabActiva, setTabActiva] = useState<TabType>('dashboard');

  const tabs = [
    {
      id: 'dashboard' as TabType,
      nombre: 'Dashboard',
      icono: <Activity className="h-5 w-5" />,
    },
    {
      id: 'receta' as TabType,
      nombre: 'Receta Electrónica',
      icono: <FileText className="h-5 w-5" />,
    },
    {
      id: 'farmacia' as TabType,
      nombre: 'Farmacia',
      icono: <Pill className="h-5 w-5" />,
    },
    {
      id: 'facturacion' as TabType,
      nombre: 'Facturación',
      icono: <DollarSign className="h-5 w-5" />,
    },
    {
      id: 'configuracion' as TabType,
      nombre: 'Configuración',
      icono: <Settings className="h-5 w-5" />,
    },
    {
      id: 'logs' as TabType,
      nombre: 'Logs',
      icono: <FileSearch className="h-5 w-5" />,
    },
  ];

  const renderContenido = () => {
    switch (tabActiva) {
      case 'dashboard':
        return <DashboardIntegraciones />;
      case 'receta':
        return <RecetaElectronica />;
      case 'farmacia':
        return <Farmacia />;
      case 'facturacion':
        return <Facturacion />;
      case 'configuracion':
        return <Configuracion />;
      case 'logs':
        return <Logs />;
      default:
        return <DashboardIntegraciones />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">
            Integraciones
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Gestión de integraciones con sistemas externos (PACS, LIS, Receta Electrónica, Farmacia, CFDI, ERP)
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
          <nav className="-mb-px flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setTabActiva(tab.id)}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
                  ${
                    tabActiva === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                {tab.icono}
                {tab.nombre}
              </button>
            ))}
          </nav>
        </div>

        {/* Contenido */}
        <div>{renderContenido()}</div>
      </div>
    </div>
  );
};

export default Integraciones;
