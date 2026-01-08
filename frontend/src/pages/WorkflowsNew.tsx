import React, { useState, useEffect, useMemo } from 'react'
import { Dialog, DialogContent, DialogTitle } from '@mui/material'
import { listWorkflows, createWorkflow, deleteWorkflow, Workflow } from '@/services/workflowService'
import WorkflowBuilder from '@/components/workflow/WorkflowBuilder'
import { Node, Edge } from '@xyflow/react'
import {
  Sparkles,
  Plus,
  Search,
  Play,
  Pencil,
  Trash2,
  Workflow as WorkflowIcon,
  Bot,
} from 'lucide-react'

export default function WorkflowsNew() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [openBuilder, setOpenBuilder] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null)
  const [newWorkflowDialog, setNewWorkflowDialog] = useState(false)
  const [newWorkflowName, setNewWorkflowName] = useState('')
  const [newWorkflowDescription, setNewWorkflowDescription] = useState('')

  useEffect(() => {
    loadWorkflows()
  }, [])

  const loadWorkflows = async () => {
    try {
      setLoading(true)
      const data = await listWorkflows()
      setWorkflows(data)
    } catch (error) {
      console.error('Error loading workflows:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateWorkflow = async () => {
    if (!newWorkflowName.trim()) return

    try {
      const workflowId = `workflow_${Date.now()}`
      const newWorkflow = await createWorkflow({
        workflow_id: workflowId,
        name: newWorkflowName,
        description: newWorkflowDescription,
        nodes: [],
        edges: [],
        config: {},
        variables: {},
      })

      setWorkflows([newWorkflow, ...workflows])
      setNewWorkflowDialog(false)
      setNewWorkflowName('')
      setNewWorkflowDescription('')
      
      // Abrir el builder con el nuevo workflow
      setSelectedWorkflow(newWorkflow)
      setOpenBuilder(true)
    } catch (error) {
      console.error('Error creating workflow:', error)
      alert('Error al crear el workflow')
    }
  }

  const handleEditWorkflow = (workflow: Workflow) => {
    setSelectedWorkflow(workflow)
    setOpenBuilder(true)
  }

  const handleDeleteWorkflow = async (workflowId: string) => {
    if (!confirm('¿Estás seguro de eliminar este workflow?')) return

    try {
      await deleteWorkflow(workflowId)
      setWorkflows(workflows.filter((w) => w.workflow_id !== workflowId))
    } catch (error) {
      console.error('Error deleting workflow:', error)
      alert('Error al eliminar el workflow')
    }
  }

  const handleSaveWorkflow = async (nodes: Node[], edges: Edge[]) => {
    if (!selectedWorkflow) return

    try {
      // Aquí llamarías al endpoint de actualización
      console.log('Saving workflow:', { nodes, edges })
      setOpenBuilder(false)
      loadWorkflows()
    } catch (error) {
      console.error('Error saving workflow:', error)
      alert('Error al guardar el workflow')
    }
  }

  const filteredWorkflows = workflows.filter(
    (w) =>
      w.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      w.description?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success'
      case 'draft':
        return 'warning'
      case 'inactive':
        return 'error'
      default:
        return 'default'
    }
  }

  const metrics = useMemo(() => {
    const total = workflows.length
    const activos = workflows.filter((w) => w.status === 'active').length
    const borradores = workflows.filter((w) => w.status === 'draft').length
    return { total, activos, borradores }
  }, [workflows])

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#4EAAC8] via-[#5BB5D3] to-[#68C0DE] p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-center">
          <div className="flex-1 text-white space-y-3">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel IA</p>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-white/15 backdrop-blur">
                <WorkflowIcon className="h-7 w-7" />
              </div>
              <h1 className="text-4xl font-extrabold leading-tight">Workflows & Agentes IA</h1>
            </div>
            <p className="text-white/85">
              Crea y gestiona workflows automatizados con agentes de inteligencia artificial.
            </p>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <MetricCard label="Workflows Totales" value={metrics.total} />
              <MetricCard label="Activos" value={metrics.activos} />
              <MetricCard label="Borradores" value={metrics.borradores} />
            </div>
          </div>
          <div className="flex flex-shrink-0 items-start">
            <button
              onClick={() => setNewWorkflowDialog(true)}
              className="inline-flex items-center gap-2 rounded-2xl border border-white/30 bg-white/10 px-6 py-3 text-white shadow-lg shadow-black/10 backdrop-blur transition hover:bg-white/15"
            >
              <Plus className="h-5 w-5" />
              Nuevo Workflow
            </button>
          </div>
        </div>
        <div className="absolute inset-y-0 right-0 hidden w-1/3 translate-x-12 overflow-hidden opacity-40 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.35),_transparent_60%)]" />
          <div className="absolute -bottom-10 right-10 h-48 w-48 rounded-full bg-white/25 blur-3xl" />
        </div>
      </section>

      {/* Search */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            className="w-full rounded-2xl border border-slate-200 bg-white px-10 py-3 text-sm shadow-sm focus:border-[#4EAAC8] focus:ring-2 focus:ring-[#4EAAC8]/20 outline-none"
            placeholder="Buscar workflows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button
          onClick={loadWorkflows}
          className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm hover:border-slate-300"
        >
          Recargar
        </button>
      </div>

      {/* Workflows Grid */}
      {loading ? (
        <div className="text-slate-500">Cargando workflows...</div>
      ) : filteredWorkflows.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-10 text-center shadow-sm">
          <Bot className="mx-auto h-10 w-10 text-slate-400 mb-3" />
          <p className="text-lg font-semibold text-slate-800 mb-1">No hay workflows</p>
          <p className="text-sm text-slate-500 mb-4">
            {searchTerm
              ? 'No se encontraron workflows con ese criterio de búsqueda'
              : 'Crea tu primer workflow para comenzar'}
          </p>
          {!searchTerm && (
            <button
              onClick={() => setNewWorkflowDialog(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#4EAAC8] to-[#5BB5D3] px-4 py-2 text-white font-semibold shadow-md"
            >
              <Plus className="h-4 w-4" />
              Crear Primer Workflow
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filteredWorkflows.map((workflow) => (
            <div
              key={workflow.id}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="min-w-0">
                  <p className="text-lg font-semibold text-slate-900 truncate">{workflow.name}</p>
                  <p className="text-sm text-slate-500 line-clamp-2">
                    {workflow.description || 'Sin descripción'}
                  </p>
                </div>
                <StatusPill status={workflow.status} />
              </div>

              <div className="flex flex-wrap gap-2 mb-3">
                {workflow.category && (
                  <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600">
                    {workflow.category}
                  </span>
                )}
                <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600">
                  {workflow.nodes?.length || 0} nodos
                </span>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>Versión: {workflow.version || '1.0'}</span>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <button
                  onClick={() => handleEditWorkflow(workflow)}
                  className="inline-flex items-center gap-1 rounded-lg bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200"
                >
                  <Pencil className="h-4 w-4" />
                  Editar
                </button>
                <button className="inline-flex items-center gap-1 rounded-lg bg-emerald-100 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-200">
                  <Play className="h-4 w-4" />
                  Ejecutar
                </button>
                <button
                  onClick={() => handleDeleteWorkflow(workflow.workflow_id)}
                  className="ml-auto inline-flex items-center gap-1 rounded-lg bg-rose-100 px-3 py-2 text-sm font-medium text-rose-700 hover:bg-rose-200"
                >
                  <Trash2 className="h-4 w-4" />
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Dialog: Nuevo Workflow */}
      {newWorkflowDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Nuevo workflow</p>
                <h3 className="text-xl font-bold text-slate-900">Crear Workflow</h3>
              </div>
              <button
                onClick={() => setNewWorkflowDialog(false)}
                className="rounded-full p-2 hover:bg-slate-100 text-slate-500"
              >
                ×
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre</label>
                <input
                  className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-[#4EAAC8] focus:ring-2 focus:ring-[#4EAAC8]/20 outline-none"
                  value={newWorkflowName}
                  onChange={(e) => setNewWorkflowName(e.target.value)}
                  placeholder="Ej: Triaje inteligente"
                  autoFocus
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Descripción</label>
                <textarea
                  className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-[#4EAAC8] focus:ring-2 focus:ring-[#4EAAC8]/20 outline-none"
                  value={newWorkflowDescription}
                  onChange={(e) => setNewWorkflowDescription(e.target.value)}
                  rows={3}
                  placeholder="Breve descripción del workflow"
                />
              </div>
              <button
                onClick={handleCreateWorkflow}
                disabled={!newWorkflowName.trim()}
                className="w-full rounded-xl bg-gradient-to-r from-[#4EAAC8] to-[#5BB5D3] px-4 py-3 text-white font-semibold shadow-md disabled:opacity-60"
              >
                Crear Workflow
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dialog: Workflow Builder */}
      <Dialog open={openBuilder} onClose={() => setOpenBuilder(false)} maxWidth="xl" fullWidth>
        <DialogTitle>{selectedWorkflow?.name || 'Workflow'}</DialogTitle>
        <DialogContent sx={{ p: 0, height: '80vh' }}>
          {selectedWorkflow && (
            <WorkflowBuilder
              workflowId={selectedWorkflow.workflow_id}
              initialNodes={selectedWorkflow.nodes || []}
              initialEdges={selectedWorkflow.edges || []}
              onSave={handleSaveWorkflow}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl bg-white/10 p-4 backdrop-blur ring-1 ring-white/20 text-white">
      <p className="text-xs uppercase tracking-wide text-white/70">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  )
}

function StatusPill({ status }: { status?: string }) {
  const map: Record<string, string> = {
    active: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    draft: 'bg-amber-100 text-amber-700 border-amber-200',
    inactive: 'bg-slate-100 text-slate-700 border-slate-200',
  }
  const cls = map[status || ''] || 'bg-slate-100 text-slate-700 border-slate-200'
  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-semibold capitalize ${cls}`}>
      {status || 'draft'}
    </span>
  )
}
