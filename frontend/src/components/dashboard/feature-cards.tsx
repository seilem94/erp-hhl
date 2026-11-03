import { Link } from '@tanstack/react-router'
import { Icon } from '@/components/ui/icon'

const exampleSummary = {
  projects: 1,
  projectGoal: 70,
  operational: 84000,
  projectExpenses: 161800,
}

const currency = new Intl.NumberFormat('es-CL', {
  style: 'currency', currency: 'CLP', maximumFractionDigits: 0,
})

function ProjectsCard() {
  return (
    <article aria-labelledby="projects-title" className="feature-card relative overflow-hidden border border-brand-navy bg-brand-navy text-white">
      <div className="pointer-events-none absolute -top-8 -right-8 size-48 rounded-full border border-white/5" aria-hidden="true" />
      <div className="flex items-center justify-between">
        <span className="card-icon bg-white/10 text-blue-200"><Icon name="blueprint" className="size-6" /></span>
        <span className="rounded-full border border-white/15 px-2.5 py-1 text-[10px] font-medium tracking-wider text-slate-300 uppercase">Obras</span>
      </div>
      <h3 id="projects-title" className="mt-5 text-xl font-semibold tracking-tight">Proyectos y Obras</h3>
      <p className="mt-2 text-sm text-slate-400">Cada proyecto, un paso adelante.</p>
      <div className="mt-7 flex items-baseline gap-2.5" aria-label={`${exampleSummary.projects} de ${exampleSummary.projectGoal} obras`}>
        <span className="text-[2.75rem] leading-none font-semibold tracking-tight">{exampleSummary.projects}</span>
        <span className="text-2xl font-medium text-slate-400">/ {exampleSummary.projectGoal}</span>
      </div>
      <div className="mt-5">
        <progress className="project-progress block h-1.5 w-full overflow-hidden rounded-full" value={exampleSummary.projects} max={exampleSummary.projectGoal} aria-label="Progreso de obras" />
        <p className="mt-2.5 text-xs text-slate-400">Obras en seguimiento</p>
      </div>
      <Link to="/proyectos" className="card-button mt-7 justify-between border border-white/15 bg-white/5 text-white hover:bg-white/10">
        Ir a Obras <Icon name="arrow-right" className="size-4" />
      </Link>
    </article>
  )
}

function ExpensesCard() {
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
          <summary className="flex cursor-pointer list-none items-center gap-1.5 rounded-lg border border-white/20 px-2.5 py-2 text-[11px] font-medium hover:bg-white/10">
            Accesos rápidos <Icon name="chevron-down" className="size-3 transition-transform group-open:rotate-180" />
          </summary>
          <div className="absolute right-0 top-full z-10 mt-2 w-48 rounded-xl border border-brand-border bg-white p-1.5 text-brand-navy shadow-lg">
            <Link to="/gastos" className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-xs hover:bg-brand-tint"><Icon name="plus" className="size-4" /> Registrar gasto</Link>
            <Link to="/gastos" className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-xs hover:bg-brand-tint"><Icon name="receipt" className="size-4" /> Consultar gastos</Link>
          </div>
        </details>
      </div>
      <h3 id="expenses-title" className="mt-5 text-xl font-semibold tracking-tight">Registro de Gastos</h3>
      <p className="mt-2 text-sm text-blue-100">Los pequeños gastos también cuentan.</p>
      <p className="mt-7 text-[2.5rem] leading-none font-semibold tracking-tight tabular-nums">{currency.format(exampleSummary.operational + exampleSummary.projectExpenses)}</p>
      <p className="mt-3 text-xs text-blue-100">Total reciente</p>
      <div className="mt-auto pt-7">
        <Link to="/gastos" className="card-button justify-center gap-2 bg-white text-brand-deep-blue shadow-sm hover:bg-blue-50">
          <Icon name="plus" className="size-4" /> Registrar Gasto
        </Link>
      </div>
    </article>
  )
}

function FinancesCard() {
  const total = exampleSummary.operational + exampleSummary.projectExpenses
  const categories = [
    { label: 'Gastos Operativos (OPEX)', value: exampleSummary.operational, color: 'bg-brand-navy' },
    { label: 'Obras (CapEx)', value: exampleSummary.projectExpenses, color: 'bg-brand-blue' },
  ]

  return (
    <article aria-labelledby="finances-title" className="feature-card border border-brand-border bg-white">
      <div className="flex items-center justify-between">
        <span className="card-icon bg-brand-canvas text-brand-navy"><Icon name="chart" className="size-6" /></span>
        <span className="text-[10px] font-medium tracking-wider text-slate-500 uppercase">Resumen</span>
      </div>
      <h3 id="finances-title" className="mt-5 text-xl font-semibold tracking-tight">Finanzas Rápidas</h3>
      <p className="mt-2 text-sm text-slate-500">Una mirada clara a tus gastos.</p>
      <div className="my-7 grid gap-5" role="img" aria-label={`Distribución de gastos: operación ${currency.format(exampleSummary.operational)}, obras ${currency.format(exampleSummary.projectExpenses)}.`}>
        {categories.map(({ label, value, color }) => (
          <div key={label}>
            <div className="mb-2.5 flex items-center justify-between gap-2 text-[11px] sm:text-xs">
              <span className="text-slate-500">{label}</span>
              <span className="font-semibold tabular-nums">{currency.format(value)}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-brand-canvas"><div className={`h-full rounded-full ${color}`} style={{ width: `${value / total * 100}%` }} /></div>
          </div>
        ))}
      </div>
      <div className="mt-auto flex items-center justify-between gap-2 border-t border-brand-border pt-5 text-sm">
        <span className="text-slate-500">Total reciente</span>
        <span className="font-semibold tabular-nums">{currency.format(total)}</span>
      </div>
    </article>
  )
}

export function FeatureCards() {
  return (
    <section aria-labelledby="overview-title" className="page-container pt-4">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h2 id="overview-title" className="text-lg font-semibold tracking-tight">Tu operación, en un vistazo</h2>
        <span className="flex items-center gap-2 rounded-full border border-brand-border bg-white px-3 py-1.5 text-[11px] text-slate-500"><span className="size-1.5 rounded-full bg-slate-400" />Datos de ejemplo</span>
      </div>
      <div className="grid gap-5 lg:grid-cols-3 lg:gap-6">
        <ProjectsCard />
        <ExpensesCard />
        <FinancesCard />
      </div>
      <p className="mt-5 flex items-start gap-2 text-xs leading-5 text-slate-500"><Icon name="check" className="mt-0.5 size-4 shrink-0 text-brand-blue" />Obras, gastos y finanzas. Todo en un mismo lugar.</p>
    </section>
  )
}
