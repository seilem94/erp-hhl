import { useQueries } from '@tanstack/react-query'
import { expenseQueryOptions, useExpenses, useProjects } from '@/hooks/queries'
import { sumClp } from '@/utils/clp'

export function useDashboardMetrics() {
  const projects = useProjects()
  const operational = useExpenses()
  const projectExpenses = useQueries({
    queries: projects.data?.map((project) => expenseQueryOptions(project.id)) ?? [],
  })
  const capexReady = projects.isSuccess && projectExpenses.every((query) => query.isSuccess)
  const operationalTotal = operational.isSuccess ? sumClp(operational.data.map((expense) => expense.amount)) : null
  const projectTotal = capexReady ? sumClp(projectExpenses.flatMap((query) => query.data?.map((expense) => expense.amount) ?? [])) : null
  const loadingExpenses = projects.isPending || operational.isPending || projectExpenses.some((query) => query.isPending)
  const error = projects.error ?? operational.error ?? projectExpenses.find((query) => query.error)?.error ?? null
  const isFetching = projects.isFetching || operational.isFetching || projectExpenses.some((query) => query.isFetching)

  function refetch() {
    void projects.refetch()
    void operational.refetch()
    for (const query of projectExpenses) void query.refetch()
  }

  return {
    projectCount: projects.isSuccess ? projects.data.length : null,
    completedCount: projects.isSuccess ? projects.data.filter((project) => project.status === 'completed').length : null,
    operationalTotal,
    projectTotal,
    total: operationalTotal !== null && projectTotal !== null ? sumClp([operationalTotal, projectTotal]) : null,
    expenseCount: operational.isSuccess && capexReady
      ? operational.data.length + projectExpenses.reduce((count, query) => count + (query.data?.length ?? 0), 0)
      : null,
    loadingProjects: projects.isPending,
    loadingExpenses,
    error,
    isFetching,
    refetch,
  }
}
