import { useState } from 'react'
import { useProjects } from '@/hooks/queries'
import { PageHeading } from '@/components/page-heading'
import { ExpenseForm } from '@/components/expenses/expense-form'
import { ExpenseHistory } from '@/components/expenses/expense-history'
import { QueryError } from '@/components/ui/feedback'

export function ExpensesPage() {
  const projects = useProjects()
  const [historyProjectId, setHistoryProjectId] = useState<string | null>(null)

  return (
    <div className="page-container py-10 sm:py-14">
      <PageHeading title="Registro de Gastos" description="Registra tus compras en terreno y asígnalas a una obra o a los gastos generales de tu equipo." />
      <div className="max-w-3xl">
        {projects.isError && <div className="mb-5"><QueryError message={`${projects.error.message} Si no necesitas asociar una obra, puedes registrar un gasto operativo.`} onRetry={() => { void projects.refetch() }} retrying={projects.isFetching} /></div>}
        <ExpenseForm projects={projects.data ?? []} projectsLoading={projects.isPending} projectsUnavailable={projects.isError && !projects.data} onRegistered={(expense) => setHistoryProjectId(expense.project_id ?? null)} />
        <ExpenseHistory projects={projects.data ?? []} projectId={historyProjectId} onProjectChange={setHistoryProjectId} />
      </div>
    </div>
  )
}
