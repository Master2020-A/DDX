import React, { useEffect, useMemo, useState } from "react";
import api from "@/lib/api";

type UiError = { message: string; details?: any } | null;

type StudioModule = {
  id: string;
  module_id: string;
  name: string;
  description?: string | null;
  version: string;
  status: string;
  icon?: string | null;
  color?: string | null;
  category?: string | null;
  created_at: string;
  updated_at: string;
};

type CategoryItem = { id: string; name: string; icon?: string };

type StatusStyle = {
  label: string;
  classes: string;
};

type StatusFilter = "all" | "active" | "draft";

const STATUS_FILTERS: { id: StatusFilter; label: string }[] = [
  { id: "all", label: "Todos" },
  { id: "active", label: "Activos" },
  { id: "draft", label: "Borradores" },
];

const ACTIVE_STATUSES = new Set(["active", "deployed", "published"]);
const DRAFT_STATUSES = new Set(["draft", "borrador"]);

const MODULE_ID_RE = /^[a-z0-9-]+$/;

const statusStyles: Record<string, StatusStyle> = {
  draft: {
    label: "Borrador",
    classes: "border border-warning-200 bg-warning-50 text-warning-700",
  },
  borrador: {
    label: "Borrador",
    classes: "border border-warning-200 bg-warning-50 text-warning-700",
  },
  active: {
    label: "Activo",
    classes: "border border-success-200 bg-success-50 text-success-700",
  },
  deployed: {
    label: "Desplegado",
    classes: "border border-primary-200 bg-primary-50 text-primary-700",
  },
  published: {
    label: "Publicado",
    classes: "border border-primary-200 bg-primary-50 text-primary-700",
  },
  default: {
    label: "En Diseño",
    classes: "border border-executive-200 bg-executive-50 text-executive-600",
  },
};

const getStatusStyle = (value?: string): StatusStyle => {
  if (!value) return statusStyles.default;
  const key = value.toLowerCase();
  return statusStyles[key] ?? statusStyles.default;
};

const getModuleInitials = (value: string) => {
  if (!value) return "";
  return value
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((segment) => segment[0]?.toUpperCase())
    .join("");
};

const formatDate = (iso?: string) => {
  if (!iso) return "Sin fecha";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "Sin fecha";
  return date.toLocaleDateString("es-MX", {
    month: "short",
    day: "numeric",
  });
};

type ModuleCardProps = {
  module: StudioModule;
  onView: (module: StudioModule) => void;
};

const ModuleCard: React.FC<ModuleCardProps> = ({ module, onView }) => {
  const { label, classes } = getStatusStyle(module.status);
  const initials = getModuleInitials(module.name);
  const moduleColor = module.color || "#0ea5e9";
  const updatedLabel = formatDate(module.updated_at || module.created_at);

  return (
    <div className="group relative overflow-hidden rounded-[28px] border border-white/80 bg-white/90 p-6 shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:shadow-executive-lg">
      <div
        className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          backgroundImage: "linear-gradient(135deg, rgba(14,165,233,0.08), rgba(14,165,233,0.02))",
        }}
      />

      <div className="relative flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className="flex h-14 w-14 items-center justify-center rounded-2xl text-lg font-semibold text-white shadow-lg"
            style={{
              backgroundImage: `linear-gradient(135deg, ${moduleColor}, rgba(8,47,73,0.9))`,
            }}
          >
            {initials}
          </div>

          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.35em] text-executive-400">
              {module.category || "General"}
            </p>
            <h3 className="text-xl font-semibold text-executive-900">{module.name}</h3>
            <p className="text-sm text-executive-500">{module.module_id}</p>
          </div>
        </div>

        <span className={`inline-flex items-center rounded-full px-3 py-1 text-[11px] font-semibold ${classes}`}>
          {label}
        </span>
      </div>

      <p className="relative mt-4 text-sm leading-relaxed text-executive-600 min-h-[60px]">
        {module.description || "Sin descripción registrada para este módulo."}
      </p>

      <div className="relative mt-6 flex flex-wrap items-center justify-between gap-3 text-xs text-executive-500">
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full border border-slate-200 bg-white px-3 py-1 font-semibold text-executive-600">
            v{module.version}
          </span>
          <span className="rounded-full bg-slate-100/80 px-3 py-1 font-semibold text-executive-500">
            Actualizado {updatedLabel}
          </span>
        </div>

        <button
          className="inline-flex items-center gap-2 rounded-full border border-transparent bg-primary-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-500"
          onClick={() => onView(module)}
        >
          Ver detalles
        </button>
      </div>
    </div>
  );
};

const DDXStudio: React.FC = () => {
  const [modules, setModules] = useState<StudioModule[]>([]);
  const [categoriesPayload, setCategoriesPayload] = useState<{ categories: CategoryItem[] } | null>(null);
  const [fieldTypesPayload, setFieldTypesPayload] = useState<any>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<UiError>(null);

  const [openCreate, setOpenCreate] = useState(false);
  const [creating, setCreating] = useState(false);

  const [moduleId, setModuleId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<string>("");
  const [color, setColor] = useState<string>("#0ea5e9");

  const [searchTerm, setSearchTerm] = useState("");
  const [showMetadata, setShowMetadata] = useState(false);

  const categories = useMemo(() => categoriesPayload?.categories ?? [], [categoriesPayload]);

  const resetCreateForm = () => {
    setModuleId("");
    setName("");
    setDescription("");
    setCategory("");
    setColor("#0ea5e9");
  };

  const loadAll = async () => {
    setLoading(true);
    setError(null);

    const [mods, cats, ftypes] = await Promise.allSettled([
      api.get("/studio/modules"),
      api.get("/studio/categories"),
      api.get("/studio/field-types"),
    ]);

    if (cats.status === "fulfilled") setCategoriesPayload(cats.value.data);
    if (ftypes.status === "fulfilled") setFieldTypesPayload(ftypes.value.data);

    if (mods.status === "fulfilled") {
      setModules(mods.value.data);
    } else {
      const e: any = mods.reason;
      const msg = e?.response?.data?.detail || e?.message || "Error cargando módulos";
      setError({ message: String(msg), details: e?.response?.data });
      setModules([]);
    }

    setLoading(false);
  };

  useEffect(() => {
    loadAll();
  }, []);

  const validateCreate = (): string | null => {
    const mid = moduleId.trim();
    const nm = name.trim();

    if (!mid) return "ID del módulo es requerido";
    if (!MODULE_ID_RE.test(mid)) return "ID debe usar solo minúsculas, números y guiones";
    if (!nm) return "Nombre es requerido";
    return null;
  };

  const handleCreate = async () => {
    const validation = validateCreate();
    if (validation) {
      setError({ message: validation });
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const payload = {
        module_id: moduleId.trim(),
        name: name.trim(),
        description: description.trim(),
        version: "1.0.0",
        icon: null,
        color,
        category: category || null,
        models: [],
        endpoints: [],
        forms: [],
      };

      await api.post("/studio/modules", payload);

      setOpenCreate(false);
      resetCreateForm();
      await loadAll();
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || "Error creando módulo";
      setError({ message: String(msg), details: e?.response?.data });
    } finally {
      setCreating(false);
    }
  };

  const filteredModules = useMemo(() => {
    if (!searchTerm) return modules;
    const query = searchTerm.toLowerCase();
    return modules.filter((module) => {
      const haystack = [module.name, module.module_id, module.description, module.category]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    });
  }, [modules, searchTerm]);

  const studioStats = useMemo(() => {
    const statusCounter = modules.reduce<Record<string, number>>((acc, item) => {
      const key = (item.status || "draft").toLowerCase();
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});

    const categoriesSet = modules.reduce<Set<string>>((set, module) => {
      if (module.category) set.add(module.category);
      return set;
    }, new Set());

    const latest = modules.reduce((ts, module) => {
      const value = new Date(module.updated_at || module.created_at).getTime();
      if (Number.isNaN(value)) return ts;
      return Math.max(ts, value);
    }, 0);

    return {
      total: modules.length,
      drafts: (statusCounter.draft || 0) + (statusCounter.borrador || 0),
      active:
        (statusCounter.active || 0) +
        (statusCounter.deployed || 0) +
        (statusCounter.published || 0),
      categories: categoriesSet.size,
      updated: latest ? formatDate(new Date(latest).toISOString()) : "—",
    };
  }, [modules]);

  const fieldTypesCount = useMemo(() => {
    if (!fieldTypesPayload) return 0;
    if (Array.isArray(fieldTypesPayload)) return fieldTypesPayload.length;
    return Object.keys(fieldTypesPayload).length;
  }, [fieldTypesPayload]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-executive-50 via-white to-white px-4 py-10 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-10">
        <section className="relative overflow-hidden rounded-[32px] bg-gradient-to-r from-primary-700 via-primary-600 to-primary-400 p-10 text-white shadow-executive-xl">
          <div className="absolute inset-y-0 right-0 -mr-16 w-72 rounded-full bg-white/10 blur-3xl" />
          <div className="relative flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
            <div className="space-y-4">
              <p className="text-xs uppercase tracking-[0.4em] text-white/70">DDX Studio</p>
              <h1 className="text-4xl font-semibold leading-tight">Constructor visual de módulos personalizados</h1>
              <p className="max-w-2xl text-lg text-white/80">
                Diseña, versiona y despliega módulos clínicos con una experiencia moderna centrada en workflows inteligentes.
              </p>
            </div>

            <div className="grid w-full grid-cols-2 gap-4 rounded-[28px] border border-white/20 bg-white/10 p-6 text-left backdrop-blur lg:w-auto">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-white/70">Módulos</p>
                <p className="text-3xl font-semibold">{studioStats.total}</p>
                <p className="text-sm text-white/70">Total diseñados</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-white/70">Activos</p>
                <p className="text-3xl font-semibold">{studioStats.active}</p>
                <p className="text-sm text-white/70">Desplegados / publicados</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-white/70">Borradores</p>
                <p className="text-3xl font-semibold">{studioStats.drafts}</p>
                <p className="text-sm text-white/70">En iteración</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-white/70">Última edición</p>
                <p className="text-3xl font-semibold">{studioStats.updated}</p>
                <p className="text-sm text-white/70">Registro reciente</p>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-executive backdrop-blur">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="relative w-full md:max-w-lg">
              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-executive-300">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
              </span>
              <input
                className="input pl-12"
                placeholder="Buscar por nombre, categoría o ID"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <button className="btn btn-secondary" onClick={loadAll} disabled={loading}>
                {loading ? "Actualizando…" : "Actualizar"}
              </button>
              <button className="btn btn-primary" onClick={() => setOpenCreate(true)}>
                Nuevo Módulo
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-2xl border border-danger-200 bg-danger-50/80 p-4 text-danger-700">
              <p className="font-semibold">Algo no salió bien</p>
              <p className="text-sm">{error.message}</p>
            </div>
          )}

          <div className="mt-6">
            {loading ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div
                    key={`skeleton-${index}`}
                    className="h-64 rounded-[28px] border border-slate-100 bg-slate-50/50 animate-pulse"
                  />
                ))}
              </div>
            ) : filteredModules.length === 0 ? (
              <div className="rounded-[28px] border border-dashed border-slate-200 bg-slate-50/60 p-12 text-center">
                <p className="text-lg font-semibold text-executive-700">Sin coincidencias</p>
                <p className="mt-2 text-sm text-executive-500">
                  Ajusta la búsqueda o crea un nuevo módulo para iniciar.
                </p>
              </div>
            ) : (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {filteredModules.map((module) => (
                  <ModuleCard key={module.id} module={module} onView={(m) => alert(JSON.stringify(m, null, 2))} />
                ))}
              </div>
            )}
          </div>
        </section>

        <section className="rounded-[28px] border border-white/70 bg-white/85 p-6 shadow-executive backdrop-blur">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-executive-400">Catálogos conectados</p>
              <h2 className="text-2xl font-semibold text-executive-900">Colecciones inteligentes de soporte</h2>
              <p className="text-sm text-executive-500">
                Los catálogos se sincronizan automáticamente para alimentar tus módulos.
              </p>
            </div>
            <button
              className="btn btn-ghost"
              onClick={() => setShowMetadata((value) => !value)}
            >
              {showMetadata ? "Ver resumen" : "Ver JSON"}
            </button>
          </div>

          <div className="mt-6 grid gap-5 lg:grid-cols-2">
            <div className="rounded-[24px] border border-slate-100 bg-white/80 p-5 shadow-inner">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-executive-900">Categorías activas</h3>
                  <p className="text-sm text-executive-500">
                    {categories.length ? `${categories.length} colecciones disponibles` : "Aún no hay categorías registradas"}
                  </p>
                </div>
              </div>

              {categories.length ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  {categories.map((item) => (
                    <span
                      key={item.id}
                      className="rounded-full bg-primary-50/80 px-3 py-1 text-sm font-medium text-primary-700"
                    >
                      {item.name}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-sm text-executive-400">
                  Una vez registres categorías, se mostrarán aquí como chips.
                </p>
              )}

              {showMetadata && (
                <pre className="mt-4 max-h-64 overflow-auto rounded-2xl bg-slate-900/90 p-4 text-xs text-white">
                  {JSON.stringify(categoriesPayload, null, 2)}
                </pre>
              )}
            </div>

            <div className="rounded-[24px] border border-slate-100 bg-white/80 p-5 shadow-inner">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-executive-900">Tipos de campos</h3>
                  <p className="text-sm text-executive-500">{fieldTypesCount} tipos configurados</p>
                </div>
              </div>

              <p className="mt-4 text-sm text-executive-500">
                Define los componentes visuales y validaciones que tus equipos podrán reutilizar al construir formularios o endpoints.
              </p>

              {showMetadata && (
                <pre className="mt-4 max-h-64 overflow-auto rounded-2xl bg-slate-900/90 p-4 text-xs text-white">
                  {JSON.stringify(fieldTypesPayload, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </section>
      </div>

      {openCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 px-4 py-8">
          <div className="w-full max-w-4xl overflow-hidden rounded-[32px] bg-white shadow-executive-xl animate-scaleIn">
            <div className="bg-gradient-to-r from-primary-700 via-primary-600 to-primary-500 px-8 py-6 text-white">
              <p className="text-xs uppercase tracking-[0.4em] text-white/80">Nuevo módulo</p>
              <h2 className="text-3xl font-semibold">Diseña un módulo personalizado</h2>
              <p className="text-sm text-white/80">Define los datos base y la identidad visual para tu nuevo módulo.</p>
            </div>

            <div className="grid gap-6 px-8 py-8 md:grid-cols-2">
              <div className="space-y-4">
                <div>
                  <label className="label">ID del módulo</label>
                  <input
                    className="input"
                    value={moduleId}
                    onChange={(event) => setModuleId(event.target.value)}
                    placeholder="vacunacion-covid"
                  />
                  <p className="mt-2 text-xs text-executive-400">
                    Usa minúsculas, números y guiones para mantener consistencia.
                  </p>
                </div>

                <div>
                  <label className="label">Nombre comercial</label>
                  <input
                    className="input"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    placeholder="Vacunación COVID-19"
                  />
                </div>

                <div>
                  <label className="label">Descripción</label>
                  <textarea
                    className="input min-h-[110px]"
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                    placeholder="Registro y seguimiento de vacunas aplicadas a pacientes"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="label">Categoría</label>
                  <select
                    className="input"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                  >
                    <option value="">Seleccionar categoría</option>
                    {categories.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="label">Color primario</label>
                  <div className="flex items-center gap-3">
                    <input
                      type="color"
                      className="h-12 w-24 cursor-pointer rounded-2xl border border-slate-200"
                      value={color}
                      onChange={(event) => setColor(event.target.value)}
                    />
                    <span className="rounded-2xl border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-executive-600">
                      {color.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-100 bg-slate-50/80 p-4 text-sm text-executive-500">
                  <p className="font-semibold text-executive-700">Checklist de despliegue</p>
                  <ul className="mt-2 list-disc space-y-1 pl-4">
                    <li>Configura modelos y endpoints antes de publicar.</li>
                    <li>Los nuevos módulos se crean en estado borrador.</li>
                    <li>Podrás editar la metadata en cualquier momento.</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-3 border-t border-slate-100 bg-slate-50/80 px-8 py-6 text-sm text-executive-500 md:flex-row md:items-center md:justify-between">
              <p>
                Se notificará al equipo cuando el módulo cambie a estado activo.
              </p>
              <div className="flex gap-3">
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setOpenCreate(false);
                    resetCreateForm();
                  }}
                  disabled={creating}
                >
                  Cancelar
                </button>
                <button className="btn btn-primary" onClick={handleCreate} disabled={creating}>
                  {creating ? "Creando módulo…" : "Crear módulo"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DDXStudio;
