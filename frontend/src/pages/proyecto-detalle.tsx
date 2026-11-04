import { Link, useParams } from '@tanstack/react-router'
import { useRef, useState } from 'react'
import { useExpenses, useProject } from '@/hooks/queries'
import { ExpenseList } from '@/components/expenses/expense-list'
import { ProjectEditForm } from '@/components/projects/project-edit-form'
import { PageHeading } from '@/components/page-heading'
import { Feedback, LoadingState, QueryError } from '@/components/ui/feedback'
import { sumDecimalAmounts } from '@/utils/decimal'
import { formatDate, formatMoney, statusLabels } from '@/utils/format'

export function ProjectDetailPage() {
  const { projectId } = useParams({ from: '/proyectos/$projectId' })
  const projectQuery = useProject(projectId)
  const expensesQuery = useExpenses(projectId, projectQuery.isSuccess && projectQuery.data !== null)
  const [editing, setEditing] = useState(false)
  const [saved, setSaved] = useState(false)
  const editButton = useRef<HTMLButtonElement>(null)

  function closeEditor() {
    setEditing(false)
    requestAnimationFrame(() => editButton.current?.focus())
  }

  if (projectQuery.isPending) {
    return <div className="page-container py-14"><PageHeading title="Detalle de Obra" description="Consulta la información y los gastos de tu proyecto." backTo="/proyectos" backLabel="Volver a Proyectos" /><LoadingState>Cargando información de la obra…</LoadingState></div>
  }
  if (projectQuery.isError && !projectQuery.data) {
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
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <button ref={editButton} type="button" className="button-primary disabled:cursor-default" disabled={editing} aria-expanded={editing} aria-controls={editing ? 'edit-project' : undefined} onClick={() => { setSaved(false); setEditing(true) }}>Editar Proyecto</button>
        {saved && <Feedback tone="success">Proyecto actualizado correctamente.</Feedback>}
      </div>
      {projectQuery.isError && <div className="mb-5"><QueryError message={projectQuery.error.message} onRetry={() => { void projectQuery.refetch() }} retrying={projectQuery.isFetching} /></div>}
      {!projectQuery.isError && projectQuery.isFetching && <div className="mb-5"><LoadingState>Actualizando información de la obra…</LoadingState></div>}
      <section aria-label="Información de la obra" aria-busy={projectQuery.isFetching} className="form-panel">
        <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div><dt className="text-sm text-slate-500 dark:text-slate-400">Cliente</dt><dd className="mt-2 break-words font-semibold text-brand-navy dark:text-slate-100">{project.client}</dd></div>
          <div><dt className="text-sm text-slate-500 dark:text-slate-400">Presupuesto</dt><dd className="money-value mt-2 font-semibold text-brand-navy dark:text-slate-100">{project.budget == null ? 'Sin presupuesto' : formatMoney(project.budget)}</dd></div>
          <div><dt className="text-sm text-slate-500 dark:text-slate-400">Estado</dt><dd className="mt-2 font-semibold text-brand-blue dark:text-blue-400">{statusLabels[project.status]}</dd></div>
          <div><dt className="text-sm text-slate-500 dark:text-slate-400">Fecha de inicio</dt><dd className="mt-2 font-semibold text-brand-navy dark:text-slate-100">{formatDate(project.start_date)}</dd></div>
        </dl>
        {project.description && <p className="mt-6 break-words border-t border-brand-border pt-5 text-sm leading-7 text-slate-600 dark:text-slate-300">{project.description}</p>}
      </section>
      {editing && <ProjectEditForm key={project.id} project={project} onClose={closeEditor} onUpdated={() => { setSaved(true); closeEditor() }} />}
      <section aria-labelledby="project-expenses-title" aria-busy={expensesQuery.isFetching} className="mt-10">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div><h2 id="project-expenses-title" className="text-xl font-semibold text-brand-navy dark:text-slate-100">Gastos de la obra (CapEx)</h2><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Todos los gastos registrados para este proyecto.</p></div>
          <div className="min-w-0 max-w-full rounded-xl border border-brand-border bg-white dark:bg-slate-900 px-5 py-3"><p className="text-xs text-slate-500 dark:text-slate-400">Total de gastos de la obra</p><p className="money-value mt-1 text-xl font-semibold text-brand-navy dark:text-slate-100">{total === null ? '—' : formatMoney(total)}</p></div>
        </div>
        {expensesQuery.isPending && <LoadingState>Cargando gastos de la obra…</LoadingState>}
        {!expensesQuery.isPending && expensesQuery.isFetching && !expensesQuery.isError && <div className="mb-4"><LoadingState>Actualizando gastos de la obra…</LoadingState></div>}
        {expensesQuery.isError && <QueryError message={expensesQuery.error.message} onRetry={() => { void expensesQuery.refetch() }} retrying={expensesQuery.isFetching} />}
        {expensesQuery.isSuccess && expenses.length === 0 && <Feedback>Esta obra todavía no tiene gastos registrados.</Feedback>}
        {expenses.length > 0 && <ExpenseList expenses={expenses} />}
        {expensesQuery.isSuccess && expenses.length > 0 && <p className="mt-4 text-xs text-slate-500 dark:text-slate-400">{expenses.length} {expenses.length === 1 ? 'gasto registrado' : 'gastos registrados'}.</p>}
        <Link to="/gastos" className="button-primary mt-6">Registrar un gasto</Link>
      </section>
    </div>
  )
}
