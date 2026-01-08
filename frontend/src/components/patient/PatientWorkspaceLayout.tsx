import { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight, User, UserCircle2 } from 'lucide-react'

export interface WorkspaceMetric {
  label: string
  value: string
  helper?: string
  tone?: 'slate' | 'violet' | 'cyan' | 'emerald' | 'amber'
}

export interface WorkspaceBreadcrumb {
  label: string
  to?: string
}

interface PatientWorkspaceLayoutProps {
  title: string
  subtitle?: string
  breadcrumbs?: WorkspaceBreadcrumb[]
  actions?: ReactNode
  metrics?: WorkspaceMetric[]
  sidebar?: ReactNode
  children: ReactNode
  heroAccent?: 'indigo' | 'cyan' | 'slate'
  patient?: {
    name?: string
    expediente?: string
    avatarUrl?: string
    tags?: string[]
  }
}

const toneClasses: Record<NonNullable<WorkspaceMetric['tone']>, string> = {
  slate: 'border-slate-200/60 bg-white/10 text-white',
  violet: 'border-violet-200/50 bg-violet-500/10 text-white',
  cyan: 'border-cyan-200/50 bg-cyan-500/10 text-white',
  emerald: 'border-emerald-200/50 bg-emerald-500/10 text-white',
  amber: 'border-amber-200/50 bg-amber-500/10 text-white',
}

const gradientByAccent: Record<NonNullable<PatientWorkspaceLayoutProps['heroAccent']>, string> = {
  indigo: 'from-slate-900 via-indigo-900 to-slate-900',
  cyan: 'from-slate-900 via-cyan-900 to-slate-900',
  slate: 'from-slate-900 via-slate-800 to-slate-900',
}

const PatientWorkspaceLayout = ({
  title,
  subtitle,
  breadcrumbs,
  actions,
  metrics,
  sidebar,
  children,
  heroAccent = 'indigo',
  patient,
}: PatientWorkspaceLayoutProps) => {
  return (
    <div className="space-y-8">
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="flex items-center text-sm text-slate-500 gap-1">
          {breadcrumbs.map((crumb, index) => (
            <span key={`${crumb.label}-${index}`} className="flex items-center gap-1">
              {crumb.to ? (
                <Link to={crumb.to} className="hover:text-indigo-500 transition-colors">
                  {crumb.label}
                </Link>
              ) : (
                <span className="text-slate-400">{crumb.label}</span>
              )}
              {index < breadcrumbs.length - 1 && <ChevronRight className="h-3.5 w-3.5" />}
            </span>
          ))}
        </nav>
      )}

      <section className={`relative overflow-hidden rounded-4xl bg-gradient-to-r ${gradientByAccent[heroAccent]} p-8 text-white shadow-2xl`}>
        <div className="flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex flex-1 items-start gap-4">
            <div className="rounded-3xl bg-white/10 p-4 backdrop-blur">
              {patient?.avatarUrl ? (
                <img src={patient.avatarUrl} alt={patient.name} className="h-16 w-16 rounded-2xl object-cover" />
              ) : (
                <UserCircle2 className="h-16 w-16 text-white/70" />
              )}
            </div>
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.35em] text-white/60">
                {patient?.expediente ? `Expediente #${patient.expediente}` : 'Expediente clínico'}
              </p>
              <h1 className="text-3xl font-semibold leading-tight">{title}</h1>
              {subtitle && <p className="text-white/80 text-sm max-w-2xl">{subtitle}</p>}
              {patient?.name && (
                <p className="text-white/70 text-sm flex items-center gap-1">
                  <User className="h-4 w-4" /> {patient.name}
                </p>
              )}
              {patient?.tags && patient.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-1">
                  {patient.tags.map((tag) => (
                    <span key={tag} className="rounded-full border border-white/30 px-3 py-1 text-xs text-white/80">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {actions && <div className="flex flex-shrink-0 justify-end">{actions}</div>}
        </div>

        {metrics && metrics.length > 0 && (
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {metrics.map((metric) => (
              <div
                key={metric.label}
                className={`rounded-3xl border p-4 backdrop-blur ${toneClasses[metric.tone || 'slate']}`}
              >
                <p className="text-xs uppercase tracking-wide text-white/70">{metric.label}</p>
                <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
                {metric.helper && <p className="text-sm text-white/70 mt-1">{metric.helper}</p>}
              </div>
            ))}
          </div>
        )}
      </section>

      <div className={`grid gap-6 ${sidebar ? 'xl:grid-cols-[320px,1fr]' : ''}`}>
        {sidebar && <aside className="space-y-6">{sidebar}</aside>}
        <section className="space-y-6">{children}</section>
      </div>
    </div>
  )}

export default PatientWorkspaceLayout
