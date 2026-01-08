import { useState } from 'react';
import { Smartphone, Bell, FileText, Settings } from 'lucide-react';
import DashboardAppMovil from '../components/app-movil/DashboardAppMovil';
import GestionNotificaciones from '../components/app-movil/GestionNotificaciones';
import GestionDocumentos from '../components/app-movil/GestionDocumentos';
import ConfiguracionApp from '../components/app-movil/ConfiguracionApp';

const AplicacionMovil = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: Smartphone },
    { id: 'notificaciones', name: 'Notificaciones', icon: Bell },
    { id: 'documentos', name: 'Documentos', icon: FileText },
    { id: 'configuracion', name: 'Configuración', icon: Settings },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">
          Aplicación Móvil
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Gestión de dispositivos móviles, notificaciones push y sincronización
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm
                  ${
                    isActive
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <Icon
                  className={`
                    -ml-0.5 mr-2 h-5 w-5
                    ${
                      isActive
                        ? 'text-blue-500 dark:text-blue-400'
                        : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'
                    }
                  `}
                />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      <div>
        {activeTab === 'dashboard' && <DashboardAppMovil />}
        {activeTab === 'notificaciones' && <GestionNotificaciones />}
        {activeTab === 'documentos' && <GestionDocumentos />}
        {activeTab === 'configuracion' && <ConfiguracionApp />}
      </div>
    </div>
  );
};

export default AplicacionMovil;
