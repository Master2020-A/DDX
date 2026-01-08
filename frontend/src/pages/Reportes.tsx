import { useState, useEffect } from 'react'
import { FileText, Users, Calendar, Activity, Download, TrendingUp, Printer } from 'lucide-react'
import api from '@/lib/api'

const Reportes = () => {
  const [stats, setStats] = useState({
    totalPacientes: 0,
    totalConsultas: 0,
    consultasHoy: 0,
    consultasMes: 0,
    pacientesPorGenero: { masculino: 0, femenino: 0, otro: 0 },
    consultasPorEstado: { completada: 0, en_proceso: 0, cancelada: 0, programada: 0 },
  })
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      console.log('🔍 Reportes: Consultando APIs...')
      const [pacientesRes, consultasRes] = await Promise.all([
        api.get('/pacientes/'),
        api.get('/consultas/')
      ])

      const pacientes = pacientesRes.data || []
      const consultas = consultasRes.data || []
      console.log('📊 Reportes: Pacientes:', pacientes.length, 'Consultas:', consultas.length)

      // Calcular estadísticas
      const hoy = new Date().toISOString().split('T')[0]
      const mesActual = new Date().toISOString().slice(0, 7)

      const consultasHoy = consultas.filter((c: any) => 
        c.fecha_hora?.startsWith(hoy)
      ).length

      const consultasMes = consultas.filter((c: any) => 
        c.fecha_hora?.startsWith(mesActual)
      ).length

      // Pacientes por género
      const generos = { masculino: 0, femenino: 0, otro: 0 }
      pacientes.forEach((p: any) => {
        if (p.genero === 'masculino') generos.masculino++
        else if (p.genero === 'femenino') generos.femenino++
        else generos.otro++
      })

      // Consultas por estado
      const estados = { completada: 0, en_proceso: 0, cancelada: 0, programada: 0 }
      consultas.forEach((c: any) => {
        if (c.estado in estados) estados[c.estado as keyof typeof estados]++
      })

      setStats({
        totalPacientes: pacientes.length,
        totalConsultas: consultas.length,
        consultasHoy,
        consultasMes,
        pacientesPorGenero: generos,
        consultasPorEstado: estados,
      })
    } catch (error) {
      console.error('❌ Reportes: Error fetching stats:', error)
      if (error.response) {
        console.error('   Status:', error.response.status)
        console.error('   URL:', error.config?.url)
      }
    } finally {
      setLoading(false)
    }
  }

  // Función helper para convertir datos a CSV
  const convertToCSV = (data: any[], headers: string[]) => {
    const headerRow = headers.join(',')
    const rows = data.map(row => 
      headers.map(header => {
        const value = row[header] || ''
        // Escapar comillas y valores con comas
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value
      }).join(',')
    )
    return [headerRow, ...rows].join('\n')
  }

  // Función helper para descargar archivo
  const downloadFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Exportar reporte general
  const exportarReporteGeneral = async () => {
    try {
      setExporting(true)
      
      const content = `REPORTE GENERAL DEL SISTEMA
Generado el: ${new Date().toLocaleString('es-MX')}

RESUMEN GENERAL
Total de Pacientes: ${stats.totalPacientes}
Total de Consultas: ${stats.totalConsultas}
Consultas Hoy: ${stats.consultasHoy}
Consultas Este Mes: ${stats.consultasMes}

PACIENTES POR GÉNERO
Masculino: ${stats.pacientesPorGenero.masculino}
Femenino: ${stats.pacientesPorGenero.femenino}
Otro: ${stats.pacientesPorGenero.otro}

CONSULTAS POR ESTADO
Completadas: ${stats.consultasPorEstado.completada}
En Proceso: ${stats.consultasPorEstado.en_proceso}
Programadas: ${stats.consultasPorEstado.programada}
Canceladas: ${stats.consultasPorEstado.cancelada}
`

      downloadFile(content, `reporte-general-${new Date().toISOString().split('T')[0]}.txt`)
    } catch (error) {
      console.error('Error exportando reporte:', error)
      alert('Error al exportar el reporte')
    } finally {
      setExporting(false)
    }
  }

  // Exportar reporte de pacientes
  const exportarReportePacientes = async () => {
    try {
      setExporting(true)
      const response = await api.get('/pacientes/')
      const pacientes = response.data || []
      
      const headers = ['numero_expediente', 'nombre_completo', 'fecha_nacimiento', 'genero', 'tipo_sangre', 'telefono', 'email']
      const csv = convertToCSV(pacientes, headers)
      
      downloadFile(csv, `reporte-pacientes-${new Date().toISOString().split('T')[0]}.csv`)
    } catch (error) {
      console.error('Error exportando pacientes:', error)
      alert('Error al exportar el reporte de pacientes')
    } finally {
      setExporting(false)
    }
  }

  // Exportar reporte de consultas
  const exportarReporteConsultas = async () => {
    try {
      setExporting(true)
      const response = await api.get('/consultas/')
      const consultas = response.data || []
      
      const headers = ['fecha_hora', 'tipo_consulta', 'motivo_consulta', 'estado']
      const csv = convertToCSV(consultas, headers)
      
      downloadFile(csv, `reporte-consultas-${new Date().toISOString().split('T')[0]}.csv`)
    } catch (error) {
      console.error('Error exportando consultas:', error)
      alert('Error al exportar el reporte de consultas')
    } finally {
      setExporting(false)
    }
  }

  // Exportar reporte de diagnósticos
  const exportarReporteDiagnosticos = async () => {
    try {
      setExporting(true)
      const response = await api.get('/diagnosticos/')
      const diagnosticos = response.data || []
      
      const headers = ['descripcion', 'codigo_cie10', 'tipo_diagnostico', 'created_at']
      const csv = convertToCSV(diagnosticos, headers)
      
      downloadFile(csv, `reporte-diagnosticos-${new Date().toISOString().split('T')[0]}.csv`)
    } catch (error) {
      console.error('Error exportando diagnósticos:', error)
      alert('Error al exportar el reporte de diagnósticos')
    } finally {
      setExporting(false)
    }
  }

  // Función helper para imprimir HTML
  const imprimirHTML = (html: string) => {
    const ventanaImpresion = window.open('', '_blank', 'width=800,height=600')
    if (ventanaImpresion) {
      ventanaImpresion.document.write(html)
      ventanaImpresion.document.close()
      ventanaImpresion.focus()
      
      // Esperar a que cargue el contenido antes de imprimir
      setTimeout(() => {
        ventanaImpresion.print()
      }, 250)
    }
  }

  // Imprimir reporte general
  const imprimirReporteGeneral = () => {
    const fecha = new Date().toLocaleDateString('es-MX', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Reporte General - DDX</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            padding: 40px;
            color: #333;
          }
          .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #6366f1;
            padding-bottom: 20px;
          }
          .header h1 {
            color: #6366f1;
            margin: 0;
            font-size: 28px;
          }
          .fecha {
            color: #666;
            font-size: 14px;
            margin-top: 10px;
          }
          .section {
            margin: 30px 0;
            page-break-inside: avoid;
          }
          .section h2 {
            color: #4f46e5;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
            font-size: 20px;
          }
          .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 15px;
          }
          .stat-card {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #6366f1;
          }
          .stat-label {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 5px;
          }
          .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #1f2937;
          }
          .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #e5e7eb;
          }
          .detail-row:last-child {
            border-bottom: none;
          }
          .detail-label {
            font-weight: 500;
            color: #4b5563;
          }
          .detail-value {
            font-weight: bold;
            color: #1f2937;
          }
          @media print {
            body {
              padding: 20px;
            }
            .no-print {
              display: none;
            }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>📊 REPORTE GENERAL DEL SISTEMA</h1>
          <div class="fecha">Generado el: ${fecha}</div>
        </div>

        <div class="section">
          <h2>Resumen General</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">Total de Pacientes</div>
              <div class="stat-value">${stats.totalPacientes}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Total de Consultas</div>
              <div class="stat-value">${stats.totalConsultas}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Consultas Hoy</div>
              <div class="stat-value">${stats.consultasHoy}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Consultas Este Mes</div>
              <div class="stat-value">${stats.consultasMes}</div>
            </div>
          </div>
        </div>

        <div class="section">
          <h2>Pacientes por Género</h2>
          <div class="detail-row">
            <span class="detail-label">Masculino</span>
            <span class="detail-value">${stats.pacientesPorGenero.masculino}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Femenino</span>
            <span class="detail-value">${stats.pacientesPorGenero.femenino}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Otro</span>
            <span class="detail-value">${stats.pacientesPorGenero.otro}</span>
          </div>
        </div>

        <div class="section">
          <h2>Consultas por Estado</h2>
          <div class="detail-row">
            <span class="detail-label">Completadas</span>
            <span class="detail-value">${stats.consultasPorEstado.completada}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">En Proceso</span>
            <span class="detail-value">${stats.consultasPorEstado.en_proceso}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Programadas</span>
            <span class="detail-value">${stats.consultasPorEstado.programada}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Canceladas</span>
            <span class="detail-value">${stats.consultasPorEstado.cancelada}</span>
          </div>
        </div>

        <script>
          window.onafterprint = function() {
            window.close();
          }
        </script>
      </body>
      </html>
    `

    imprimirHTML(html)
  }

  // Imprimir reporte de pacientes
  const imprimirReportePacientes = async () => {
    try {
      setExporting(true)
      const response = await api.get('/pacientes/')
      const pacientes = response.data || []

      const fecha = new Date().toLocaleDateString('es-MX', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })

      const filasHTML = pacientes.map((p: any, index: number) => `
        <tr>
          <td>${index + 1}</td>
          <td>${p.numero_expediente || '-'}</td>
          <td>${p.nombre_completo || '-'}</td>
          <td>${p.fecha_nacimiento || '-'}</td>
          <td>${p.genero || '-'}</td>
          <td>${p.tipo_sangre || '-'}</td>
          <td>${p.telefono || '-'}</td>
        </tr>
      `).join('')

      const html = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>Reporte de Pacientes - DDX</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              padding: 30px;
              color: #333;
            }
            .header {
              text-align: center;
              margin-bottom: 30px;
              border-bottom: 3px solid #6366f1;
              padding-bottom: 15px;
            }
            h1 {
              color: #6366f1;
              margin: 0;
            }
            .fecha {
              color: #666;
              font-size: 14px;
              margin-top: 10px;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin-top: 20px;
            }
            th {
              background: #6366f1;
              color: white;
              padding: 12px;
              text-align: left;
              font-weight: 600;
            }
            td {
              padding: 10px;
              border-bottom: 1px solid #e5e7eb;
            }
            tr:hover {
              background: #f9fafb;
            }
            .total {
              margin-top: 20px;
              text-align: right;
              font-weight: bold;
              color: #4f46e5;
            }
            @media print {
              body { padding: 15px; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>📋 REPORTE DE PACIENTES</h1>
            <div class="fecha">${fecha}</div>
          </div>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Expediente</th>
                <th>Nombre Completo</th>
                <th>Fecha Nacimiento</th>
                <th>Género</th>
                <th>Tipo Sangre</th>
                <th>Teléfono</th>
              </tr>
            </thead>
            <tbody>
              ${filasHTML}
            </tbody>
          </table>
          <div class="total">Total de pacientes: ${pacientes.length}</div>
          <script>
            window.onafterprint = function() { window.close(); }
          </script>
        </body>
        </html>
      `

      imprimirHTML(html)
    } catch (error) {
      console.error('Error imprimiendo pacientes:', error)
      alert('Error al generar el reporte de pacientes')
    } finally {
      setExporting(false)
    }
  }

  // Imprimir reporte de consultas
  const imprimirReporteConsultas = async () => {
    try {
      setExporting(true)
      const response = await api.get('/consultas/')
      const consultas = response.data || []

      const fecha = new Date().toLocaleDateString('es-MX', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })

      const filasHTML = consultas.map((c: any, index: number) => `
        <tr>
          <td>${index + 1}</td>
          <td>${c.fecha_hora ? new Date(c.fecha_hora).toLocaleString('es-MX') : '-'}</td>
          <td>${c.tipo_consulta || '-'}</td>
          <td>${c.motivo_consulta || '-'}</td>
          <td><span class="badge badge-${c.estado}">${c.estado || '-'}</span></td>
        </tr>
      `).join('')

      const html = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>Reporte de Consultas - DDX</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              padding: 30px;
              color: #333;
            }
            .header {
              text-align: center;
              margin-bottom: 30px;
              border-bottom: 3px solid #10b981;
              padding-bottom: 15px;
            }
            h1 {
              color: #10b981;
              margin: 0;
            }
            .fecha {
              color: #666;
              font-size: 14px;
              margin-top: 10px;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin-top: 20px;
            }
            th {
              background: #10b981;
              color: white;
              padding: 12px;
              text-align: left;
              font-weight: 600;
            }
            td {
              padding: 10px;
              border-bottom: 1px solid #e5e7eb;
            }
            .badge {
              padding: 4px 12px;
              border-radius: 12px;
              font-size: 12px;
              font-weight: 600;
            }
            .badge-completada { background: #d1fae5; color: #065f46; }
            .badge-en_proceso { background: #fef3c7; color: #92400e; }
            .badge-programada { background: #dbeafe; color: #1e40af; }
            .badge-cancelada { background: #fee2e2; color: #991b1b; }
            .total {
              margin-top: 20px;
              text-align: right;
              font-weight: bold;
              color: #059669;
            }
            @media print {
              body { padding: 15px; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>📅 REPORTE DE CONSULTAS</h1>
            <div class="fecha">${fecha}</div>
          </div>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Fecha y Hora</th>
                <th>Tipo</th>
                <th>Motivo</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              ${filasHTML}
            </tbody>
          </table>
          <div class="total">Total de consultas: ${consultas.length}</div>
          <script>
            window.onafterprint = function() { window.close(); }
          </script>
        </body>
        </html>
      `

      imprimirHTML(html)
    } catch (error) {
      console.error('Error imprimiendo consultas:', error)
      alert('Error al generar el reporte de consultas')
    } finally {
      setExporting(false)
    }
  }

  // Imprimir reporte de diagnósticos
  const imprimirReporteDiagnosticos = async () => {
    try {
      setExporting(true)
      const response = await api.get('/diagnosticos/')
      const diagnosticos = response.data || []

      const fecha = new Date().toLocaleDateString('es-MX', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })

      const filasHTML = diagnosticos.map((d: any, index: number) => `
        <tr>
          <td>${index + 1}</td>
          <td>${d.descripcion || '-'}</td>
          <td>${d.codigo_cie10 || '-'}</td>
          <td>${d.tipo_diagnostico || '-'}</td>
          <td>${d.created_at ? new Date(d.created_at).toLocaleDateString('es-MX') : '-'}</td>
        </tr>
      `).join('')

      const html = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>Reporte de Diagnósticos - DDX</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              padding: 30px;
              color: #333;
            }
            .header {
              text-align: center;
              margin-bottom: 30px;
              border-bottom: 3px solid #8b5cf6;
              padding-bottom: 15px;
            }
            h1 {
              color: #8b5cf6;
              margin: 0;
            }
            .fecha {
              color: #666;
              font-size: 14px;
              margin-top: 10px;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin-top: 20px;
            }
            th {
              background: #8b5cf6;
              color: white;
              padding: 12px;
              text-align: left;
              font-weight: 600;
            }
            td {
              padding: 10px;
              border-bottom: 1px solid #e5e7eb;
            }
            .total {
              margin-top: 20px;
              text-align: right;
              font-weight: bold;
              color: #7c3aed;
            }
            @media print {
              body { padding: 15px; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>🔬 REPORTE DE DIAGNÓSTICOS</h1>
            <div class="fecha">${fecha}</div>
          </div>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Descripción</th>
                <th>Código CIE-10</th>
                <th>Tipo</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              ${filasHTML}
            </tbody>
          </table>
          <div class="total">Total de diagnósticos: ${diagnosticos.length}</div>
          <script>
            window.onafterprint = function() { window.close(); }
          </script>
        </body>
        </html>
      `

      imprimirHTML(html)
    } catch (error) {
      console.error('Error imprimiendo diagnósticos:', error)
      alert('Error al generar el reporte de diagnósticos')
    } finally {
      setExporting(false)
    }
  }

  const reportCards = [
    {
      title: 'Total Pacientes',
      value: stats.totalPacientes,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%'
    },
    {
      title: 'Total Consultas',
      value: stats.totalConsultas,
      icon: Calendar,
      color: 'bg-green-500',
      change: '+8%'
    },
    {
      title: 'Consultas Hoy',
      value: stats.consultasHoy,
      icon: Activity,
      color: 'bg-purple-500',
      change: '-'
    },
    {
      title: 'Consultas Este Mes',
      value: stats.consultasMes,
      icon: TrendingUp,
      color: 'bg-orange-500',
      change: '+15%'
    },
  ]

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Cargando reportes...</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reportes</h1>
          <p className="text-gray-600 mt-2">Estadísticas y análisis del sistema</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={imprimirReporteGeneral}
            disabled={exporting}
            className="btn btn-secondary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Printer size={16} className="mr-2" />
            Imprimir PDF
          </button>
          <button 
            onClick={exportarReporteGeneral}
            disabled={exporting}
            className="btn btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download size={16} className="mr-2" />
            {exporting ? 'Exportando...' : 'Exportar CSV'}
          </button>
        </div>
      </div>

      {/* Cards principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {reportCards.map((card) => {
          const Icon = card.icon
          return (
            <div key={card.title} className="card">
              <div className="flex items-center justify-between mb-2">
                <div className={`${card.color} p-3 rounded-lg`}>
                  <Icon className="text-white" size={24} />
                </div>
                <span className="text-sm text-green-600 font-medium">{card.change}</span>
              </div>
              <p className="text-sm font-medium text-gray-600">{card.title}</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Distribución por Género */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pacientes por Género</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-700">Masculino</span>
                <span className="font-bold text-blue-600">{stats.pacientesPorGenero.masculino}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ width: `${(stats.pacientesPorGenero.masculino / stats.totalPacientes) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-700">Femenino</span>
                <span className="font-bold text-pink-600">{stats.pacientesPorGenero.femenino}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-pink-500 h-2 rounded-full" 
                  style={{ width: `${(stats.pacientesPorGenero.femenino / stats.totalPacientes) * 100}%` }}
                />
              </div>
            </div>
            {stats.pacientesPorGenero.otro > 0 && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-700">Otro</span>
                  <span className="font-bold text-purple-600">{stats.pacientesPorGenero.otro}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full" 
                    style={{ width: `${(stats.pacientesPorGenero.otro / stats.totalPacientes) * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Consultas por Estado */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Consultas por Estado</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-700">Completadas</span>
                <span className="font-bold text-green-600">{stats.consultasPorEstado.completada}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: `${(stats.consultasPorEstado.completada / stats.totalConsultas) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-700">En Proceso</span>
                <span className="font-bold text-yellow-600">{stats.consultasPorEstado.en_proceso}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full" 
                  style={{ width: `${(stats.consultasPorEstado.en_proceso / stats.totalConsultas) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-700">Programadas</span>
                <span className="font-bold text-blue-600">{stats.consultasPorEstado.programada}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ width: `${(stats.consultasPorEstado.programada / stats.totalConsultas) * 100}%` }}
                />
              </div>
            </div>
            {stats.consultasPorEstado.cancelada > 0 && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-700">Canceladas</span>
                  <span className="font-bold text-red-600">{stats.consultasPorEstado.cancelada}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-red-500 h-2 rounded-full" 
                    style={{ width: `${(stats.consultasPorEstado.cancelada / stats.totalConsultas) * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Reportes disponibles */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Reportes Disponibles</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all">
            <FileText className="text-primary-600 mb-2" size={24} />
            <h3 className="font-medium text-gray-900 mb-1">Reporte de Pacientes</h3>
            <p className="text-sm text-gray-600 mb-3">Lista completa de pacientes registrados</p>
            <div className="flex gap-2">
              <button
                onClick={imprimirReportePacientes}
                disabled={exporting}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Printer size={14} />
                PDF
              </button>
              <button
                onClick={exportarReportePacientes}
                disabled={exporting}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download size={14} />
                CSV
              </button>
            </div>
          </div>
          
          <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all">
            <Calendar className="text-primary-600 mb-2" size={24} />
            <h3 className="font-medium text-gray-900 mb-1">Reporte de Consultas</h3>
            <p className="text-sm text-gray-600 mb-3">Historial de consultas médicas</p>
            <div className="flex gap-2">
              <button
                onClick={imprimirReporteConsultas}
                disabled={exporting}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Printer size={14} />
                PDF
              </button>
              <button
                onClick={exportarReporteConsultas}
                disabled={exporting}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download size={14} />
                CSV
              </button>
            </div>
          </div>
          
          <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all">
            <Activity className="text-primary-600 mb-2" size={24} />
            <h3 className="font-medium text-gray-900 mb-1">Reporte de Diagnósticos</h3>
            <p className="text-sm text-gray-600 mb-3">Estadísticas de diagnósticos</p>
            <div className="flex gap-2">
              <button
                onClick={imprimirReporteDiagnosticos}
                disabled={exporting}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Printer size={14} />
                PDF
              </button>
              <button
                onClick={exportarReporteDiagnosticos}
                disabled={exporting}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download size={14} />
                CSV
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reportes
