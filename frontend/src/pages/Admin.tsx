import React, { useState } from 'react';
import { Shield, Users, Key, Activity, Settings } from 'lucide-react';
import DashboardSeguridad from '../components/admin/DashboardSeguridad';
import GestionUsuarios from '../components/admin/GestionUsuarios';
import GestionRoles from '../components/admin/GestionRoles';
import LogsAuditoria from '../components/admin/LogsAuditoria';

type TabType = 'dashboard' | 'usuarios' | 'roles' | 'auditoria';

const Admin: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  const tabs = [
    { id: 'dashboard' as TabType, label: 'Dashboard', icon: Activity },
    { id: 'usuarios' as TabType, label: 'Usuarios', icon: Users },
    { id: 'roles' as TabType, label: 'Roles y Permisos', icon: Key },
    { id: 'auditoria' as TabType, label: 'Auditoría', icon: Shield },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Settings className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Panel de Administración</h1>
                <p className="text-sm text-gray-500">Gestión de seguridad y usuarios</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm
                    ${
                      activeTab === tab.id
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <DashboardSeguridad />}
        {activeTab === 'usuarios' && <GestionUsuarios />}
        {activeTab === 'roles' && <GestionRoles />}
        {activeTab === 'auditoria' && <LogsAuditoria />}
      </div>
    </div>
  );
};

export default Admin;
