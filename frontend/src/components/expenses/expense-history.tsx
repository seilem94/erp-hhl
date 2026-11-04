import type { ProjectResponse } from '@/api/types'
import { useExpenses } from '@/hooks/queries'
import { Feedback, QueryError } from '@/components/ui/feedback'
import { ExpenseList } from '@/components/expenses/expense-list'

type ExpenseHistoryProps = { projectId: string | null; onProjectChange: (id: string | null) => void; projects: ProjectResponse[] }

export function ExpenseHistory({ projectId, onProjectChange, projects }: ExpenseHistoryProps) {
  const query = useExpenses(projectId)
  const expenses = query.data ? [...query.data].sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 10) : []
  return (
    <section aria-labelledby="expense-history-title" aria-busy={query.isFetching} className="mt-10 min-w-0">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div><h2 id="expense-history-title" className="text-xl font-semibold tracking-tight">Últimos gastos registrados</h2><p className="mt-2 text-sm text-slate-500">Hasta 10 registros de la cuenta seleccionada.</p></div>
        <div className="w-full sm:w-64"><label htmlFor="history-project" className="mb-2 block text-sm text-slate-600">Consultar gastos de</label><select id="history-project" className="form-input" value={projectId ?? ''} onChange={(event) => onProjectChange(event.target.value || null)}>
          <option value="">Gastos operativos (OPEX)</option>
          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
        </select></div>
      </div>
      <div className="grid gap-3">
        {query.isPending && <Feedback>Cargando gastos…</Feedback>}
        {query.isError && <QueryError message={query.error.message} onRetry={() => { void query.refetch() }} retrying={query.isFetching} />}
        {query.isSuccess && expenses.length === 0 && <Feedback>No hay gastos registrados en esta cuenta.</Feedback>}
        {expenses.length > 0 && <ExpenseList expenses={expenses} />}
      </div>
    </section>
  )
}
