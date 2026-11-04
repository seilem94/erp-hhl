import { useState } from 'react'
import type { ProjectResponse } from '@/api/types'
import { useExpenses } from '@/hooks/queries'
import { Feedback, QueryError } from '@/components/ui/feedback'
import { ExpenseList } from '@/components/expenses/expense-list'

type ExpenseHistoryProps = { projectId: string | null; onProjectChange: (id: string | null) => void; projects: ProjectResponse[] }

export function ExpenseHistory({ projectId, onProjectChange, projects }: ExpenseHistoryProps) {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const invalidRange = Boolean(startDate && endDate && startDate > endDate)
  const query = useExpenses(projectId, !invalidRange, { start_date: startDate || undefined, end_date: endDate || undefined })
  const expenses = query.data ? [...query.data].sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 10) : []
  return (
    <section aria-labelledby="expense-history-title" aria-busy={query.isFetching} className="mt-10 min-w-0">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div><h2 id="expense-history-title" className="text-xl font-semibold tracking-tight">Últimos gastos registrados</h2><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Hasta 10 registros de la cuenta y período seleccionados.</p></div>
        <div className="w-full sm:w-64"><label htmlFor="history-project" className="mb-2 block text-sm text-slate-600 dark:text-slate-300">Consultar gastos de</label><select id="history-project" className="form-input" value={projectId ?? ''} onChange={(event) => onProjectChange(event.target.value || null)}>
          <option value="">Gastos operativos (OPEX)</option>
          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
        </select></div>
      </div>
      <div role="group" aria-label="Filtrar gastos por fecha" className="mb-5 grid items-end gap-4 sm:grid-cols-3">
        <div><label htmlFor="expenses-from" className="mb-2 block text-sm text-slate-600 dark:text-slate-300">Desde</label><input id="expenses-from" type="date" className="form-input" value={startDate} onChange={(event) => setStartDate(event.target.value)} aria-invalid={invalidRange} aria-describedby={invalidRange ? 'expenses-range-error' : undefined} /></div>
        <div><label htmlFor="expenses-until" className="mb-2 block text-sm text-slate-600 dark:text-slate-300">Hasta</label><input id="expenses-until" type="date" className="form-input" value={endDate} onChange={(event) => setEndDate(event.target.value)} aria-invalid={invalidRange} aria-describedby={invalidRange ? 'expenses-range-error' : undefined} /></div>
        <button type="button" className="button-secondary" disabled={!startDate && !endDate} onClick={() => { setStartDate(''); setEndDate('') }}>Limpiar fechas</button>
      </div>
      <div className="grid gap-3">
        {invalidRange && <div id="expenses-range-error"><Feedback tone="error">La fecha Desde no puede ser posterior a Hasta.</Feedback></div>}
        {!invalidRange && query.isPending && <Feedback>Cargando gastos…</Feedback>}
        {!invalidRange && query.isError && <QueryError message={query.error.message} onRetry={() => { void query.refetch() }} retrying={query.isFetching} />}
        {!invalidRange && query.isSuccess && expenses.length === 0 && <Feedback>No hay gastos registrados para esta cuenta y período.</Feedback>}
        {!invalidRange && expenses.length > 0 && <ExpenseList expenses={expenses} />}
      </div>
    </section>
  )
}
