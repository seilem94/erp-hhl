import { Link } from '@tanstack/react-router'
import { Icon } from '@/components/ui/icon'
import { QueryError } from '@/components/ui/feedback'
import { useDashboardMetrics } from '@/hooks/dashboard'
import { formatMoney } from '@/utils/format'

type CardProps = { metrics: ReturnType<typeof useDashboardMetrics> }

function Metric({ value, loading }: { value: string | null; loading: boolean }) {
  if (loading) {
    return <span role="status" aria-label="Cargando métricas" className="inline-block h-10 w-36 rounded-lg bg-current/10 align-middle motion-safe:animate-pulse" />
  }
  return <span>{value ?? '—'}</span>
}

function ProjectsCard({ metrics }: CardProps) {
  const { projectCount, completedCount, loadingProjects } = metrics
  return (
    <article aria-labelledby="projects-title" className="feature-card relative overflow-hidden border border-brand-navy bg-brand-navy text-white">
      <div className="pointer-events-none absolute -top-8 -right-8 size-48 rounded-full border border-white/5" aria-hidden="true" />
      <div className="flex items-center justify-between">
        <span className="card-icon bg-white/10 text-blue-200"><Icon name="blueprint" className="size-6" /></span>
        <span className="rounded-full border border-white/15 px-2.5 py-1 text-[10px] font-medium tracking-wider text-slate-300 uppercase">Obras</span>
      </div>
      <h3 id="projects-title" className="mt-5 text-xl font-semibold tracking-tight">Proyectos y Obras</h3>
      <p className="mt-2 text-sm text-slate-400">Cada proyecto, un paso adelante.</p>
      <p className="money-value mt-7 text-[2.75rem] leading-none font-semibold tracking-tight"><Metric value={projectCount === null ? null : String(projectCount)} loading={loadingProjects} /></p>
      <p className="mt-3 text-xs text-slate-400">Obras registradas</p>
      <div className="mt-5">
        {projectCount !== null && projectCount > 0 && completedCount !== null
          ? <progress className="project-progress block h-1.5 w-full overflow-hidden rounded-full" value={completedCount} max={projectCount} aria-label="Obras completadas" />
          : <div aria-hidden="true" className="h-1.5 rounded-full bg-white/10" />}
        <p className="mt-2.5 text-xs text-slate-400">
          {loadingProjects ? 'Consultando obras…' : projectCount === null ? 'Información no disponible' : projectCount === 0 ? 'Aún no hay obras registradas.' : `${completedCount} de ${projectCount} obras completadas`}
        </p>
      </div>
      <Link to="/proyectos" className="card-button mt-auto justify-between border border-white/15 bg-white/5 text-white hover:bg-white/10">
        Ir a Obras <Icon name="arrow-right" className="size-4" />
      </Link>
    </article>
  )
}

function ExpensesCard({ metrics }: CardProps) {
  return (
    <article aria-labelledby="expenses-title" className="feature-card expense-card text-white">
      <div className="flex items-center justify-between gap-2">
        <span className="card-icon bg-white/15"><Icon name="receipt" className="size-6" /></span>
        <details className="quick-actions group relative" onKeyDown={(event) => {
          if (event.key === 'Escape') {
            event.currentTarget.open = false
            event.currentTarget.querySelector('summary')?.focus()
          }
        }} onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) event.currentTarget.open = false }}>
          <summary className="flex min-h-11 cursor-pointer list-none items-center gap-1.5 rounded-lg border border-white/20 px-2.5 py-2 text-[11px] font-medium hover:bg-white/10">
            Accesos rápidos <Icon name="chevron-down" className="size-3 transition-transform group-open:rotate-180" />
          </summary>
          <div className="absolute right-0 top-full z-10 mt-2 w-48 rounded-xl border border-brand-border bg-white dark:bg-slate-900 p-1.5 text-brand-navy dark:text-slate-100 shadow-lg">
            <Link to="/gastos" className="flex min-h-11 items-center gap-2 rounded-lg px-3 py-2.5 text-xs hover:bg-brand-tint"><Icon name="plus" className="size-4" /> Registrar gasto</Link>
            <Link to="/gastos" className="flex min-h-11 items-center gap-2 rounded-lg px-3 py-2.5 text-xs hover:bg-brand-tint"><Icon name="receipt" className="size-4" /> Consultar gastos</Link>
          </div>
        </details>
      </div>
      <h3 id="expenses-title" className="mt-5 text-xl font-semibold tracking-tight">Registro de Gastos</h3>
      <p className="mt-2 text-sm text-white">Los pequeños gastos también cuentan.</p>
      <p className="money-value mt-7 text-[2.5rem] leading-none font-semibold tracking-tight"><Metric value={metrics.total === null ? null : formatMoney(metrics.total)} loading={metrics.loadingExpenses} /></p>
      <p className="mt-3 text-xs text-white">Gastos acumulados</p>
      <p className="mt-3 text-xs text-white">{metrics.expenseCount === null ? metrics.loadingExpenses ? 'Consultando registros…' : 'Información no disponible' : `${metrics.expenseCount} ${metrics.expenseCount === 1 ? 'gasto registrado' : 'gastos registrados'}`}</p>
      <div className="mt-auto pt-7">
        <Link to="/gastos" className="card-button justify-center gap-2 bg-white text-brand-deep-blue shadow-sm hover:bg-blue-50">
          <Icon name="plus" className="size-4" /> Registrar Gasto
        </Link>
      </div>
    </article>
  )
}

function FinancesCard({ metrics }: CardProps) {
  const total = metrics.total === null ? null : Number(metrics.total)
  const categories = [
    { label: 'Gastos Operativos (OPEX)', value: metrics.operationalTotal, color: 'bg-brand-navy dark:bg-slate-400' },
    { label: 'Obras (CapEx)', value: metrics.projectTotal, color: 'bg-brand-blue' },
  ]
  const chartLabel = metrics.total === null ? 'Resumen financiero todavía no disponible.' : `Distribución de gastos: operación ${formatMoney(metrics.operationalTotal ?? '0')}, obras ${formatMoney(metrics.projectTotal ?? '0')}.`

  return (
    <article aria-labelledby="finances-title" className="feature-card border border-brand-border bg-white dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <span className="card-icon bg-brand-canvas text-brand-navy dark:text-slate-100"><Icon name="chart" className="size-6" /></span>
        <span className="text-[10px] font-medium tracking-wider text-slate-500 dark:text-slate-400 uppercase">Resumen</span>
      </div>
      <h3 id="finances-title" className="mt-5 text-xl font-semibold tracking-tight">Finanzas Rápidas</h3>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Una mirada clara a tus gastos.</p>
      <div className="my-7 grid gap-5" role="img" aria-label={chartLabel}>
        {categories.map(({ label, value, color }) => (
          <div key={label}>
            <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2 text-[11px] sm:text-xs">
              <span className="text-slate-500 dark:text-slate-400">{label}</span>
              <span className="money-value font-semibold">{metrics.loadingExpenses ? '…' : value === null ? '—' : formatMoney(value)}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-brand-canvas"><div className={`h-full rounded-full ${color}`} style={{ width: `${total !== null && total > 0 && value !== null ? Math.max(0, Math.min(100, Number(value) / total * 100)) : 0}%` }} /></div>
          </div>
        ))}
      </div>
      <div className="mt-auto flex flex-wrap items-center justify-between gap-2 border-t border-brand-border pt-5 text-sm">
        <span className="text-slate-500 dark:text-slate-400">Total registrado</span>
        <span className="money-value font-semibold">{metrics.loadingExpenses ? '…' : metrics.total === null ? '—' : formatMoney(metrics.total)}</span>
      </div>
    </article>
  )
}

export function FeatureCards() {
  const metrics = useDashboardMetrics()
  const status = metrics.error ? 'Resumen incompleto' : metrics.isFetching ? 'Actualizando…' : 'Datos consultados'
  return (
    <section aria-labelledby="overview-title" aria-busy={metrics.isFetching} className="page-container pt-4">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h2 id="overview-title" className="text-lg font-semibold tracking-tight">Tu operación, en un vistazo</h2>
        <span className="flex items-center gap-2 rounded-full border border-brand-border bg-white dark:bg-slate-900 px-3 py-1.5 text-[11px] text-slate-500 dark:text-slate-400"><span className={`size-1.5 rounded-full ${metrics.error ? 'bg-amber-500' : 'bg-brand-blue'}`} />{status}</span>
      </div>
      {metrics.error && <div className="mb-5"><QueryError message={`No pudimos cargar todo el resumen. ${metrics.error.message}`} onRetry={metrics.refetch} retrying={metrics.isFetching} /></div>}
      <div className="grid gap-5 lg:grid-cols-3 lg:gap-6">
        <ProjectsCard metrics={metrics} />
        <ExpensesCard metrics={metrics} />
        <FinancesCard metrics={metrics} />
      </div>
      <p className="mt-5 flex items-start gap-2 text-xs leading-5 text-slate-500 dark:text-slate-400"><Icon name="check" className="mt-0.5 size-4 shrink-0 text-brand-blue dark:text-blue-400" />Obras, gastos y finanzas. Todo en un mismo lugar.</p>
    </section>
  )
}
