import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useThemeStore } from '@/store/themeStore'
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  LogOut,
  Activity,
  Menu,
  X,
  Hotel,
  ArrowRightLeft,
  Moon,
  Sun,
  Search,
  Brain,
  BarChart3,
  Settings,
  Shield,
  Database,
  Smartphone,
  Link2,
  Key,
  Video,
  UserCircle,
  Building2,
  ArrowLeftRight,
  Microscope,
  Download,
  Wrench,
  ShoppingBag,
  FlaskConical,
  Stethoscope,
  ClipboardList,
  FileEdit,
  Pill,
  HeartPulse,
  FolderOpen,
  MessageSquare,
  Zap,
  BookOpen,
  Lock
} from 'lucide-react'
import { useEffect, useState } from 'react'
import GlobalSearchPalette from './GlobalSearchPalette'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { ChevronDown, ChevronRight } from 'lucide-react'

const Layout = () => {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [interopOpen, setInteropOpen] = useState(false)
  const { mode, toggle } = useThemeStore()
  
  useKeyboardShortcuts(() => setSearchOpen(true))

  // Sincronizar la clase `dark` en el elemento raíz con el modo actual
  useEffect(() => {
    const root = document.documentElement
    if (mode === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [mode])

  const navigation = [
    // Módulos principales
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Pacientes', href: '/pacientes', icon: Users },
    { name: 'Consultas', href: '/consultas', icon: Activity },
    { name: 'Telemedicina', href: '/telemedicina', icon: Video },
    { name: 'Interconsultas', href: '/interconsultas', icon: ArrowRightLeft },
    { name: 'Imágenes Médicas', href: '/imagenes', icon: Microscope },
    
    // Inteligencia Artificial
    { name: 'IA Médica', href: '/ia-medica', icon: Brain },
    { name: 'Workflows IA', href: '/workflows', icon: Brain },
    
    // Herramientas y desarrollo
    { name: 'DDX Studio', href: '/ddx-studio', icon: Wrench },
    { name: 'Marketplace', href: '/marketplace', icon: ShoppingBag },
    
    // Portal y aplicaciones
    { name: 'Portal del Paciente', href: '/portal-paciente', icon: UserCircle },
    { name: 'Aplicación Móvil', href: '/app-movil', icon: Smartphone },
    
    // Integraciones
    { name: 'Integraciones', href: '/integraciones', icon: Link2 },
    { name: 'N8N Integration', href: '/n8n', icon: Zap },
    { name: 'API Pública', href: '/api-publica', icon: Key },
    
    // Análisis y reportes
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Reportes', href: '/reportes', icon: FileText },
    
    // Administración
    { name: 'Cumplimiento Normativo', href: '/cumplimiento', icon: Shield },
    { name: 'Backups y Recuperación', href: '/backups', icon: Database },
    { name: 'Multi-Tenancy', href: '/multi-tenancy', icon: Building2 },
  ]

  const interoperabilidadItems = [
    { name: 'Observaciones FHIR', href: '/fhir-observations', icon: Microscope },
    { name: 'Importar desde FHIR', href: '/fhir-import', icon: Download },
    { name: 'Interoperabilidad FHIR', href: '/ia/interoperabilidad', icon: Link2 },
    { name: 'Interoperabilidad', href: '/interoperabilidad', icon: ArrowLeftRight },
  ]

  const isActive = (path: string) => {
    return location.pathname === path
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-50">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-800 sticky top-0 z-40">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
              <div className="flex items-center ml-2 lg:ml-0">
                <Activity className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-xl font-bold text-gray-900 dark:text-gray-50">DDX</span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-50">{user?.nombre_completo}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{user?.rol}</p>
              </div>
              <button
                onClick={() => setSearchOpen(true)}
                className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 rounded-md"
                title="Buscar (Ctrl+K)"
                aria-label="Abrir búsqueda global"
              >
                <Search size={20} />
              </button>
              <button
                onClick={toggle}
                className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 rounded-md"
                title={mode === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
                aria-label="Cambiar tema"
              >
                {mode === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              <button
                onClick={logout}
                className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 rounded-md"
                title="Cerrar sesión"
                aria-label="Cerrar sesión"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside
          className={`
            fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800
            transform transition-transform duration-200 ease-in-out lg:translate-x-0
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            mt-16 lg:mt-0
          `}
        >
          <nav className="p-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                    ${
                      isActive(item.href)
                        ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-200'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
                    }
                  `}
                >
                  <Icon size={20} className="mr-3" />
                  {item.name}
                </Link>
              )
            })}
            
            {/* Menú desplegable de Interoperabilidad */}
            <div>
              <button
                onClick={() => setInteropOpen(!interopOpen)}
                className="flex items-center justify-between w-full px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
              >
                <div className="flex items-center">
                  <ArrowLeftRight size={20} className="mr-3" />
                  Interoperabilidad
                </div>
                {interopOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>
              
              {interopOpen && (
                <div className="ml-4 mt-1 space-y-1">
                  {interoperabilidadItems.map((item) => {
                    const Icon = item.icon
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        onClick={() => setSidebarOpen(false)}
                        className={`
                          flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors
                          ${
                            isActive(item.href)
                              ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-200'
                              : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                          }
                        `}
                      >
                        <Icon size={18} className="mr-3" />
                        {item.name}
                      </Link>
                    )
                  })}
                </div>
              )}
            </div>
            
            {/* Admin Panel - Solo para administradores */}
            {user?.rol === 'admin' && (
              <>
                <div className="border-t border-gray-200 dark:border-gray-700 my-2"></div>
                <Link
                  to="/admin"
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                    ${
                      isActive('/admin')
                        ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-200'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
                    }
                  `}
                >
                  <Settings size={20} className="mr-3" />
                  Administración
                </Link>
              </>
            )}
          </nav>
        </aside>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-gray-600 bg-opacity-50 z-20 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
      
      {/* Global Search Palette */}
      <GlobalSearchPalette isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  )
}

export default Layout
