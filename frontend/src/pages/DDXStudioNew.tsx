import React, { useEffect, useState } from 'react'
import { Plus, Play, Trash2, Eye, Code, Database, FileCode, AlertCircle, CheckCircle, XCircle, Loader, Edit } from 'lucide-react'
import api from '@/lib/api'

interface Module {
  id: string
  module_id: string
  name: string
  description?: string
  version: string
  status: string
  icon?: string
  color?: string
  category?: string
  created_at: string
  updated_at: string
}

interface Field {
  name: string
  type: string
  label?: string
  required: boolean
  nullable: boolean
  unique: boolean
  indexed: boolean
  show_in_table: boolean
  show_in_form: boolean
}

interface Model {
  name: string
  table_name: string
  description?: string
  fields: Field[]
}

interface Category {
  id: string
  name: string
  icon?: string
}

const DDXStudioNew: React.FC = () => {
  const [modules, setModules] = useState<Module[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [fieldTypes, setFieldTypes] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showPreviewModal, setShowPreviewModal] = useState(false)
  const [selectedModule, setSelectedModule] = useState<Module | null>(null)
  const [previewCode, setPreviewCode] = useState<any>(null)
  const [isEditMode, setIsEditMode] = useState(false)

  // Form states
  const [formData, setFormData] = useState({
    module_id: '',
    name: '',
    description: '',
    category: '',
    color: '#3b82f6',
    models: [] as Model[]
  })

  // Model builder states
  const [currentModel, setCurrentModel] = useState<Model>({
    name: '',
    table_name: '',
    description: '',
    fields: []
  })

  const [currentField, setCurrentField] = useState<Field>({
    name: '',
    type: 'string',
    label: '',
    required: false,
    nullable: true,
    unique: false,
    indexed: false,
    show_in_table: true,
    show_in_form: true
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [modulesRes, categoriesRes, typesRes] = await Promise.all([
        api.get('/studio/modules'),
        api.get('/studio/categories'),
        api.get('/studio/field-types')
      ])
      setModules(modulesRes.data)
      setCategories(categoriesRes.data.categories || [])
      setFieldTypes(typesRes.data.types || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error cargando datos')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateModule = async () => {
    if (!formData.module_id || !formData.name) {
      setError('ID y nombre son requeridos')
      return
    }

    if (formData.models.length === 0) {
      setError('Debes agregar al menos un modelo')
      return
    }

    try {
      await api.post('/studio/modules', {
        ...formData,
        version: '1.0.0',
        endpoints: [],
        forms: []
      })
      setShowCreateModal(false)
      resetForm()
      loadData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creando módulo')
    }
  }

  const handleDeployModule = async (moduleId: string) => {
    if (!confirm('¿Desplegar este módulo? Se crearán archivos y tablas en la base de datos.')) {
      return
    }

    try {
      const response = await api.post(`/studio/modules/${moduleId}/deploy`)
      alert(`Módulo desplegado exitosamente!\n\n${JSON.stringify(response.data, null, 2)}`)
      loadData()
    } catch (err: any) {
      alert(`Error desplegando módulo: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleUndeployModule = async (moduleId: string) => {
    if (!confirm('¿Desactivar este módulo? Se eliminarán los archivos generados.')) {
      return
    }

    try {
      await api.post(`/studio/modules/${moduleId}/undeploy`)
      alert('Módulo desactivado exitosamente')
      loadData()
    } catch (err: any) {
      alert(`Error desactivando módulo: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleDeleteModule = async (moduleId: string) => {
    if (!confirm('¿Eliminar este módulo permanentemente?')) {
      return
    }

    try {
      await api.delete(`/studio/modules/${moduleId}`)
      loadData()
    } catch (err: any) {
      alert(`Error eliminando módulo: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handlePreviewCode = async (moduleId: string) => {
    try {
      const response = await api.post(`/studio/modules/${moduleId}/preview`)
      console.log('Preview response:', response.data)
      setPreviewCode(response.data)
      setShowPreviewModal(true)
    } catch (err: any) {
      console.error('Preview error:', err)
      alert(`Error generando preview: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleEditModule = async (module: Module) => {
    try {
      const response = await api.get(`/studio/modules/${module.module_id}`)
      const moduleData = response.data
      
      // Cargar datos del módulo en el formulario
      setFormData({
        module_id: moduleData.module_id,
        name: moduleData.name,
        description: moduleData.description || '',
        category: moduleData.category || '',
        color: moduleData.color || '#3b82f6',
        models: moduleData.definition?.models || []
      })
      
      setSelectedModule(module)
      setIsEditMode(true)
      setShowEditModal(true)
    } catch (err: any) {
      alert(`Error cargando módulo: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleUpdateModule = async () => {
    if (!selectedModule) return

    try {
      await api.put(`/studio/modules/${selectedModule.module_id}`, {
        ...formData,
        version: selectedModule.version,
        endpoints: [],
        forms: []
      })
      setShowEditModal(false)
      setIsEditMode(false)
      resetForm()
      loadData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error actualizando módulo')
    }
  }

  const addFieldToModel = () => {
    if (!currentField.name) {
      alert('El campo debe tener un nombre')
      return
    }

    setCurrentModel({
      ...currentModel,
      fields: [...currentModel.fields, { ...currentField }]
    })

    // Reset field form
    setCurrentField({
      name: '',
      type: 'string',
      label: '',
      required: false,
      nullable: true,
      unique: false,
      indexed: false,
      show_in_table: true,
      show_in_form: true
    })
  }

  const removeFieldFromModel = (index: number) => {
    setCurrentModel({
      ...currentModel,
      fields: currentModel.fields.filter((_, i) => i !== index)
    })
  }

  const addModelToModule = () => {
    console.log('🔵 addModelToModule llamado')
    console.log('Current model:', currentModel)
    
    if (!currentModel.name || !currentModel.table_name) {
      console.log('❌ Validación fallida: falta nombre o tabla')
      alert('El modelo debe tener nombre y nombre de tabla')
      return
    }

    if (currentModel.fields.length === 0) {
      console.log('❌ Validación fallida: sin campos')
      alert('El modelo debe tener al menos un campo')
      return
    }

    console.log('✅ Agregando modelo al módulo')
    const newModels = [...formData.models, { ...currentModel }]
    console.log('Nuevos modelos:', newModels)
    
    setFormData({
      ...formData,
      models: newModels
    })

    // Reset model form
    setCurrentModel({
      name: '',
      table_name: '',
      description: '',
      fields: []
    })
    
    console.log('✅ Modelo agregado y formulario reseteado')
  }

  const removeModelFromModule = (index: number) => {
    setFormData({
      ...formData,
      models: formData.models.filter((_, i) => i !== index)
    })
  }

  const resetForm = () => {
    setFormData({
      module_id: '',
      name: '',
      description: '',
      category: '',
      color: '#3b82f6',
      models: []
    })
    setCurrentModel({
      name: '',
      table_name: '',
      description: '',
      fields: []
    })
    setCurrentField({
      name: '',
      type: 'string',
      label: '',
      required: false,
      nullable: true,
      unique: false,
      indexed: false,
      show_in_table: true,
      show_in_form: true
    })
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { color: string; icon: any; text: string }> = {
      draft: { color: 'bg-gray-100 text-gray-700', icon: AlertCircle, text: 'Borrador' },
      active: { color: 'bg-green-100 text-green-700', icon: CheckCircle, text: 'Activo' },
      inactive: { color: 'bg-yellow-100 text-yellow-700', icon: XCircle, text: 'Inactivo' },
      deprecated: { color: 'bg-red-100 text-red-700', icon: XCircle, text: 'Obsoleto' }
    }

    const badge = badges[status] || badges.draft
    const Icon = badge.icon

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="w-3 h-3" />
        {badge.text}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  const totalModules = modules.length
  const activeModules = modules.filter(m => m.status === 'active').length
  const draftModules = modules.filter(m => m.status === 'draft').length
  const categoriesCount = new Set(modules.map(m => m.category).filter(Boolean)).size

  const heroMetrics = [
    { label: 'Módulos totales', value: totalModules },
    { label: 'Módulos activos', value: activeModules },
    { label: 'En desarrollo', value: draftModules },
    { label: 'Categorías', value: categoriesCount },
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section with Gradient */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-600 via-sky-500 to-cyan-400 p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex-1 text-white">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel de desarrollo</p>
            <h1 className="mt-3 text-4xl font-extrabold leading-tight">
              DDX Studio
            </h1>
            <p className="mt-2 max-w-2xl text-base text-white/85">
              Constructor visual de módulos personalizados. Crea, despliega y gestiona
              funcionalidades dinámicas para el sistema DDX.
            </p>
            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {heroMetrics.map((metric) => (
                <div
                  key={metric.label}
                  className="rounded-2xl bg-white/10 p-4 backdrop-blur ring-1 ring-white/20"
                >
                  <span className="text-xs uppercase tracking-wide text-white/60">
                    {metric.label}
                  </span>
                  <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-shrink-0 items-start gap-3 lg:flex-col">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center justify-center rounded-2xl border border-white/30 bg-white/10 px-6 py-3 text-white shadow-lg shadow-black/10 backdrop-blur transition hover:bg-white/15"
            >
              <Plus className="mr-2" size={20} />
              Nuevo Módulo
            </button>
          </div>
        </div>
        <div className="absolute inset-y-0 right-0 hidden w-1/3 translate-x-12 overflow-hidden opacity-40 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.4),_transparent_60%)]" />
          <div className="absolute -bottom-10 right-10 h-48 w-48 rounded-full bg-white/20 blur-3xl" />
        </div>
      </section>

      {/* Error Alert */}
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {modules.map((module) => (
          <div key={module.id} className="group relative overflow-hidden rounded-3xl border border-slate-100 bg-white/90 p-6 shadow-sm ring-1 ring-transparent transition hover:-translate-y-1 hover:border-indigo-100 hover:shadow-2xl hover:ring-indigo-100">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-slate-900">{module.name}</h3>
                <p className="text-sm text-slate-500 mt-1">{module.module_id}</p>
              </div>
              {getStatusBadge(module.status)}
            </div>

            {module.description && (
              <p className="text-sm text-slate-600 mb-4 line-clamp-2">{module.description}</p>
            )}

            <div className="flex items-center gap-2 text-xs text-slate-500 mb-4">
              <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1 font-medium text-slate-600">v{module.version}</span>
              {module.category && (
                <span className="inline-flex items-center rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 font-medium text-indigo-700">{module.category}</span>
              )}
            </div>

            <div className="flex items-center gap-2">
              {module.status === 'draft' && (
                <button
                  onClick={() => handleDeployModule(module.module_id)}
                  className="flex-1 inline-flex items-center justify-center gap-1 px-3 py-2 bg-emerald-600 text-white text-sm rounded-xl hover:bg-emerald-700 transition shadow-sm"
                >
                  <Play className="w-4 h-4" />
                  Desplegar
                </button>
              )}

              {module.status === 'active' && (
                <button
                  onClick={() => handleUndeployModule(module.module_id)}
                  className="flex-1 inline-flex items-center justify-center gap-1 px-3 py-2 bg-amber-600 text-white text-sm rounded-xl hover:bg-amber-700 transition shadow-sm"
                >
                  <XCircle className="w-4 h-4" />
                  Desactivar
                </button>
              )}

              <button
                onClick={() => handleEditModule(module)}
                className="inline-flex items-center justify-center gap-1 px-3 py-2 bg-purple-50 text-purple-700 text-sm rounded-xl hover:bg-purple-100 transition border border-purple-200"
                title="Editar módulo"
              >
                <Edit className="w-4 h-4" />
              </button>

              <button
                onClick={() => handlePreviewCode(module.module_id)}
                className="inline-flex items-center justify-center gap-1 px-3 py-2 bg-indigo-50 text-indigo-700 text-sm rounded-xl hover:bg-indigo-100 transition border border-indigo-200"
                title="Ver código"
              >
                <Eye className="w-4 h-4" />
              </button>

              <button
                onClick={() => handleDeleteModule(module.module_id)}
                className="inline-flex items-center justify-center gap-1 px-3 py-2 bg-rose-50 text-rose-700 text-sm rounded-xl hover:bg-rose-100 transition border border-rose-200"
                title="Eliminar módulo"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}

        {modules.length === 0 && (
          <div className="col-span-full text-center py-12">
            <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No hay módulos</h3>
            <p className="text-gray-600 mb-4">Crea tu primer módulo personalizado</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Plus className="w-5 h-5" />
              Crear Módulo
            </button>
          </div>
        )}
      </div>

      {/* Create Module Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold">Crear Nuevo Módulo</h2>
              <button onClick={() => { setShowCreateModal(false); resetForm() }} className="text-gray-500 hover:text-gray-700">
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Module Info */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Información del Módulo</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">ID del Módulo *</label>
                    <input
                      type="text"
                      value={formData.module_id}
                      onChange={(e) => setFormData({ ...formData, module_id: e.target.value })}
                      placeholder="mi-modulo"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Solo minúsculas, números y guiones</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Mi Módulo"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Descripción del módulo..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Seleccionar...</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                    <input
                      type="color"
                      value={formData.color}
                      onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                      className="w-full h-10 px-1 py-1 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
              </div>

              {/* Model Builder */}
              <div className="border-t border-gray-200 pt-6 space-y-4">
                <h3 className="text-lg font-semibold">Constructor de Modelos</h3>

                <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Modelo</label>
                      <input
                        type="text"
                        value={currentModel.name}
                        onChange={(e) => setCurrentModel({ ...currentModel, name: e.target.value })}
                        placeholder="Paciente"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de Tabla</label>
                      <input
                        type="text"
                        value={currentModel.table_name}
                        onChange={(e) => setCurrentModel({ ...currentModel, table_name: e.target.value })}
                        placeholder="pacientes"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Descripción del Modelo</label>
                    <input
                      type="text"
                      value={currentModel.description}
                      onChange={(e) => setCurrentModel({ ...currentModel, description: e.target.value })}
                      placeholder="Modelo para gestionar pacientes"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  {/* Field Builder */}
                  <div className="border-t border-gray-300 pt-4">
                    <h4 className="text-sm font-semibold mb-3">Agregar Campo</h4>
                    
                    <div className="grid grid-cols-3 gap-3 mb-3">
                      <div>
                        <input
                          type="text"
                          value={currentField.name}
                          onChange={(e) => setCurrentField({ ...currentField, name: e.target.value })}
                          placeholder="nombre_campo"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        />
                      </div>

                      <div>
                        <select
                          value={currentField.type}
                          onChange={(e) => setCurrentField({ ...currentField, type: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        >
                          {fieldTypes.map((type) => (
                            <option key={type.id} value={type.id}>{type.name}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <input
                          type="text"
                          value={currentField.label}
                          onChange={(e) => setCurrentField({ ...currentField, label: e.target.value })}
                          placeholder="Etiqueta"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        />
                      </div>
                    </div>

                    <div className="flex items-center gap-4 mb-3 text-sm">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={currentField.required}
                          onChange={(e) => setCurrentField({ ...currentField, required: e.target.checked })}
                          className="rounded"
                        />
                        Requerido
                      </label>

                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={currentField.unique}
                          onChange={(e) => setCurrentField({ ...currentField, unique: e.target.checked })}
                          className="rounded"
                        />
                        Único
                      </label>

                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={currentField.indexed}
                          onChange={(e) => setCurrentField({ ...currentField, indexed: e.target.checked })}
                          className="rounded"
                        />
                        Indexado
                      </label>
                    </div>

                    <button
                      onClick={addFieldToModel}
                      className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
                    >
                      Agregar Campo
                    </button>
                  </div>

                  {/* Fields List */}
                  {currentModel.fields.length > 0 && (
                    <div className="border-t border-gray-300 pt-4">
                      <h4 className="text-sm font-semibold mb-2">Campos del Modelo ({currentModel.fields.length})</h4>
                      <div className="space-y-2">
                        {currentModel.fields.map((field, index) => (
                          <div key={index} className="flex items-center justify-between bg-white p-2 rounded border border-gray-200">
                            <div className="flex items-center gap-3 text-sm">
                              <span className="font-medium">{field.name}</span>
                              <span className="text-gray-500">{field.type}</span>
                              {field.required && <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">Requerido</span>}
                              {field.unique && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Único</span>}
                            </div>
                            <button
                              onClick={() => removeFieldFromModel(index)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <button
                    onClick={addModelToModule}
                    className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
                  >
                    Agregar Modelo al Módulo
                  </button>
                </div>
              </div>

              {/* Models List */}
              {formData.models.length > 0 && (
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold mb-4">Modelos del Módulo ({formData.models.length})</h3>
                  <div className="space-y-3">
                    {formData.models.map((model, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-semibold">{model.name}</h4>
                            <p className="text-sm text-gray-600">Tabla: {model.table_name}</p>
                            <p className="text-xs text-gray-500 mt-1">{model.fields.length} campos</p>
                          </div>
                          <button
                            onClick={() => removeModelFromModule(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex items-center justify-end gap-3">
              <button
                onClick={() => { setShowCreateModal(false); setIsEditMode(false); resetForm() }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateModule}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Crear Módulo
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold">Editar Módulo</h2>
              <button onClick={() => { setShowEditModal(false); setIsEditMode(false); resetForm() }} className="text-gray-500 hover:text-gray-700">
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Module Info */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Información del Módulo</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">ID del Módulo *</label>
                    <input
                      type="text"
                      value={formData.module_id}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
                    />
                    <p className="text-xs text-gray-500 mt-1">El ID no se puede modificar</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Mi Módulo"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Descripción del módulo..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Seleccionar...</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                    <input
                      type="color"
                      value={formData.color}
                      onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                      className="w-full h-10 px-1 py-1 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
              </div>

              {/* Models List */}
              {formData.models.length > 0 && (
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold mb-4">Modelos del Módulo ({formData.models.length})</h3>
                  <div className="space-y-3">
                    {formData.models.map((model, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-semibold">{model.name}</h4>
                            <p className="text-sm text-gray-600">Tabla: {model.table_name}</p>
                            <p className="text-xs text-gray-500 mt-1">{model.fields.length} campos</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="text-sm text-yellow-600 mt-4 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    Los modelos no se pueden editar después de crear el módulo. Para modificar modelos, crea un nuevo módulo.
                  </p>
                </div>
              )}
            </div>

            <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex items-center justify-end gap-3">
              <button
                onClick={() => { setShowEditModal(false); setIsEditMode(false); resetForm() }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleUpdateModule}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Guardar Cambios
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreviewModal && previewCode && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold">Preview de Código</h2>
              <button onClick={() => { setShowPreviewModal(false); setPreviewCode(null) }} className="text-gray-500 hover:text-gray-700" title="Cerrar">
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {!previewCode.model_code && !previewCode.endpoint_code && !previewCode.component_code && !previewCode.migration_sql && (
                <div className="text-center py-8 text-gray-500">
                  <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No hay código para mostrar. El módulo debe tener al menos un modelo.</p>
                </div>
              )}
              {previewCode.model_code && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    Modelo (SQLAlchemy)
                  </h3>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {previewCode.model_code}
                  </pre>
                </div>
              )}

              {previewCode.endpoint_code && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Code className="w-5 h-5" />
                    Endpoint (FastAPI)
                  </h3>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {previewCode.endpoint_code}
                  </pre>
                </div>
              )}

              {previewCode.component_code && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <FileCode className="w-5 h-5" />
                    Componente (React)
                  </h3>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {previewCode.component_code}
                  </pre>
                </div>
              )}

              {previewCode.migration_sql && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    Migración SQL
                  </h3>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {previewCode.migration_sql}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DDXStudioNew
