import { useState } from 'react';
import { Database, Clock, AlertTriangle, FileText } from 'lucide-react';
import DashboardBackups from '../components/backups/DashboardBackups';
import GestionBackups from '../components/backups/GestionBackups';
import ProgramacionBackups from '../components/backups/ProgramacionBackups';

const BackupsRecuperacion = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: Database },
    { id: 'backups', name: 'Backups', icon: FileText },
    { id: 'programacion', name: 'Programación', icon: Clock },
    { id: 'alertas', name: 'Alertas', icon: AlertTriangle },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">
          Backups y Recuperación
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Gestión de backups, restauración y alta disponibilidad del sistema
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
        {activeTab === 'dashboard' && <DashboardBackups />}
        {activeTab === 'backups' && <GestionBackups />}
        {activeTab === 'programacion' && <ProgramacionBackups />}
        {activeTab === 'alertas' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="text-center py-12">
              <AlertTriangle className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-50">
                Sistema de Alertas
              </h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Monitoreo de alertas y notificaciones del sistema de backups
              </p>
              <p className="mt-4 text-xs text-gray-400">
                Esta funcionalidad estará disponible próximamente
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BackupsRecuperacion;
