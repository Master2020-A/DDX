import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, Activity, FileText, Calendar } from 'lucide-react'
import api from '@/lib/api'

const Dashboard = () => {
  const [stats, setStats] = useState({
    pacientes: 0,
    consultasHoy: 0,
    consultasPendientes: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        
        // Obtener total de pacientes
        const pacientesResponse = await api.get('/pacientes/')
        const totalPacientes = pacientesResponse.data?.length || 0
        
        // Obtener consultas de hoy
        const consultasResponse = await api.get('/consultas/')
        const consultas = consultasResponse.data || []
        
        const hoy = new Date().toISOString().split('T')[0]
        const consultasHoy = consultas.filter((c: any) => 
          c.fecha_hora?.startsWith(hoy)
        ).length
        
        const consultasPendientes = consultas.filter((c: any) => 
          c.estado === 'en_proceso'
        ).length
        
        setStats({
          pacientes: totalPacientes,
          consultasHoy,
          consultasPendientes,
        })
      } catch (error) {
        console.error('Error fetching dashboard stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const cards = [
    {
      title: 'Total Pacientes',
      value: stats.pacientes,
      icon: Users,
      color: 'bg-blue-500',
      link: '/pacientes',
    },
    {
      title: 'Consultas Hoy',
      value: stats.consultasHoy,
      icon: Calendar,
      color: 'bg-green-500',
      link: '/consultas',
    },
    {
      title: 'Consultas Activas',
      value: stats.consultasPendientes,
      icon: Activity,
      color: 'bg-yellow-500',
      link: '/consultas',
    },
    {
      title: 'Reportes',
      value: '-',
      icon: FileText,
      color: 'bg-purple-500',
      link: '/reportes',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Resumen general del sistema</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cards.map((card) => {
          const Icon = card.icon
          return (
            <Link
              key={card.title}
              to={card.link}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  {loading ? (
                    <div className="h-9 w-16 bg-gray-200 animate-pulse rounded mt-2"></div>
                  ) : (
                    <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
                  )}
                </div>
                <div className={`${card.color} p-3 rounded-lg`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Consultas Recientes</h2>
          <p className="text-gray-500 text-center py-8">No hay consultas registradas</p>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Accesos Rápidos</h2>
          <div className="space-y-3">
            <Link
              to="/pacientes"
              className="block p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div className="flex items-center">
                <Users className="text-primary-600 mr-3" size={20} />
                <span className="font-medium text-gray-900">Gestión de Pacientes</span>
              </div>
            </Link>
            <Link
              to="/consultas/nueva"
              className="block p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div className="flex items-center">
                <Activity className="text-primary-600 mr-3" size={20} />
                <span className="font-medium text-gray-900">Nueva Consulta</span>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
