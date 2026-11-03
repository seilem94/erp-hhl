import type { ProjectResponse } from '@/api/types'
import { useExpenses } from '@/hooks/queries'
import { Feedback, QueryError } from '@/components/ui/feedback'
import { categoryLabels, formatDate, formatMoney } from '@/utils/format'

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
        {expenses.map((expense) => <article key={expense.id} className="rounded-xl border border-brand-border bg-white p-5">
          <div className="flex items-start justify-between gap-4"><h3 className="min-w-0 break-words text-sm font-semibold">{expense.description}</h3><p className="shrink-0 text-sm font-semibold text-brand-navy tabular-nums">{formatMoney(expense.amount)}</p></div>
          <p className="mt-2 text-xs text-slate-500">{categoryLabels[expense.category]} · {formatDate(expense.date)}</p>
        </article>)}
      </div>
    </section>
  )
}
