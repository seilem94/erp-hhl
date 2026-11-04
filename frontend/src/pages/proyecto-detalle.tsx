import { Link, useParams } from '@tanstack/react-router'
import { useExpenses, useProject } from '@/hooks/queries'
import { ExpenseList } from '@/components/expenses/expense-list'
import { PageHeading } from '@/components/page-heading'
import { Feedback, QueryError } from '@/components/ui/feedback'
import { sumDecimalAmounts } from '@/utils/decimal'
import { formatDate, formatMoney, statusLabels } from '@/utils/format'

export function ProjectDetailPage() {
  const { projectId } = useParams({ from: '/proyectos/$projectId' })
  const projectQuery = useProject(projectId)
  const expensesQuery = useExpenses(projectId, projectQuery.isSuccess && projectQuery.data !== null)

  if (projectQuery.isPending) {
    return <div className="page-container py-14"><Feedback>Cargando información de la obra…</Feedback></div>
  }
  if (projectQuery.isError) {
    return <div className="page-container py-14"><PageHeading title="Detalle de Obra" description="Consulta la información y los gastos de tu proyecto." backTo="/proyectos" backLabel="Volver a Proyectos" /><QueryError message={projectQuery.error.message} onRetry={() => { void projectQuery.refetch() }} retrying={projectQuery.isFetching} /></div>
  }
  const project = projectQuery.data
  if (!project) {
    return <div className="page-container py-14"><PageHeading title="Obra no encontrada" description="La obra solicitada no está disponible en el listado de proyectos." backTo="/proyectos" backLabel="Volver a Proyectos" /></div>
  }
  const expenses = expensesQuery.data ? [...expensesQuery.data].sort((a, b) => b.date.localeCompare(a.date) || b.created_at.localeCompare(a.created_at)) : []
  const total = expensesQuery.isSuccess ? sumDecimalAmounts(expenses.map((expense) => expense.amount)) : null

  return (
    <div className="page-container py-10 sm:py-14">
      <PageHeading title={project.name} description="Información y gastos asociados a esta obra." backTo="/proyectos" backLabel="Volver a Proyectos" />
      <section aria-label="Información de la obra" aria-busy={projectQuery.isFetching} className="form-panel">
        <dl className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div><dt className="text-sm text-slate-500">Cliente</dt><dd className="mt-2 break-words font-semibold text-brand-navy">{project.client}</dd></div>
          <div><dt className="text-sm text-slate-500">Presupuesto</dt><dd className="mt-2 font-semibold text-brand-navy tabular-nums">{project.budget == null ? 'Sin presupuesto' : formatMoney(project.budget)}</dd></div>
          <div><dt className="text-sm text-slate-500">Estado</dt><dd className="mt-2 font-semibold text-brand-blue">{statusLabels[project.status]}</dd></div>
          <div><dt className="text-sm text-slate-500">Fecha de inicio</dt><dd className="mt-2 font-semibold text-brand-navy">{formatDate(project.start_date)}</dd></div>
        </dl>
        {project.description && <p className="mt-6 break-words border-t border-brand-border pt-5 text-sm leading-7 text-slate-600">{project.description}</p>}
      </section>
      <section aria-labelledby="project-expenses-title" aria-busy={expensesQuery.isFetching} className="mt-10">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div><h2 id="project-expenses-title" className="text-xl font-semibold text-brand-navy">Gastos de la obra (CapEx)</h2><p className="mt-2 text-sm text-slate-500">Todos los gastos registrados para este proyecto.</p></div>
          <div className="rounded-xl border border-brand-border bg-white px-5 py-3"><p className="text-xs text-slate-500">Total de gastos de la obra</p><p className="mt-1 text-xl font-semibold text-brand-navy tabular-nums">{total === null ? '—' : formatMoney(total)}</p></div>
        </div>
        {expensesQuery.isPending && <Feedback>Cargando gastos de la obra…</Feedback>}
        {expensesQuery.isError && <QueryError message={expensesQuery.error.message} onRetry={() => { void expensesQuery.refetch() }} retrying={expensesQuery.isFetching} />}
        {expensesQuery.isSuccess && expenses.length === 0 && <Feedback>Esta obra todavía no tiene gastos registrados.</Feedback>}
        {expenses.length > 0 && <ExpenseList expenses={expenses} />}
        {expensesQuery.isSuccess && expenses.length > 0 && <p className="mt-4 text-xs text-slate-500">{expenses.length} {expenses.length === 1 ? 'gasto registrado' : 'gastos registrados'}.</p>}
        <Link to="/gastos" className="button-primary mt-6">Registrar un gasto</Link>
      </section>
    </div>
  )
}
