import { queryOptions, useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { createProject, getProjects, updateProject } from '@/api/projects'
import { getExpenses, registerExpense } from '@/api/expenses'
import type { ApiError } from '@/api/client'
import type { CreateProjectRequest, ExpenseFilters, ExpenseResponse, ProjectResponse, RegisterExpenseRequest, UpdateProjectRequest } from '@/api/types'

export const queryKeys = {
  projects: ['projects'] as const,
  project: (projectId: string) => ['projects', 'detail', projectId] as const,
  expenses: ['expenses'] as const,
  expenseAccount: (projectId: string | null) => ['expenses', projectId] as const,
  expenseList: (projectId: string | null, filters: ExpenseFilters = {}) => ['expenses', projectId, { start_date: filters.start_date || null, end_date: filters.end_date || null }] as const,
}

function projectsQueryOptions() {
  return queryOptions<ProjectResponse[], ApiError>({
    queryKey: queryKeys.projects,
    queryFn: ({ signal }) => getProjects(signal),
    staleTime: 30000,
    networkMode: 'always',
    retry: false,
  })
}

export function useProjects() {
  return useQuery(projectsQueryOptions())
}

export function useProject(projectId: string) {
  const client = useQueryClient()
  // No individual GET in OpenAPI: resolve the detail through the shared collection.
  return useQuery<ProjectResponse | null, ApiError>({
    queryKey: queryKeys.project(projectId),
    queryFn: async () => (await client.fetchQuery(projectsQueryOptions())).find((project) => project.id === projectId) ?? null,
    // A derived snapshot must not stay fresh after the shared collection changes.
    staleTime: 0,
    networkMode: 'always',
    retry: false,
  })
}

async function cancelProjectReads(client: QueryClient, projectId?: string) {
  await client.cancelQueries({ queryKey: queryKeys.projects, exact: true })
  if (projectId) await client.cancelQueries({ queryKey: queryKeys.project(projectId), exact: true })
}

async function refreshProject(client: QueryClient, projectId?: string) {
  await client.invalidateQueries({ queryKey: queryKeys.projects, exact: true })
  if (projectId) await client.invalidateQueries({ queryKey: queryKeys.project(projectId), exact: true })
}

async function cacheProject(client: QueryClient, project: ProjectResponse) {
  // Stop older GET responses from overwriting the confirmed mutation result.
  await cancelProjectReads(client, project.id)
  client.setQueryData(queryKeys.project(project.id), project)
  client.setQueryData<ProjectResponse[]>(queryKeys.projects, (projects) => {
    if (!projects) return undefined
    return projects.some((item) => item.id === project.id)
      ? projects.map((item) => item.id === project.id ? project : item)
      : [...projects, project]
  })
  await refreshProject(client, project.id)
}

async function refreshExpenseAccount(client: QueryClient, projectId: string | null) {
  // All date ranges for this account, including the unfiltered Dashboard/detail.
  const queryKey = queryKeys.expenseAccount(projectId)
  await client.cancelQueries({ queryKey })
  await client.invalidateQueries({ queryKey })
}

export function useUpdateProject(projectId: string) {
  const client = useQueryClient()
  return useMutation<ProjectResponse, ApiError, UpdateProjectRequest>({
    mutationFn: (body) => updateProject(projectId, body),
    networkMode: 'always',
    retry: false,
    onSuccess: (project) => cacheProject(client, project),
    onError: async (error) => {
      if (!error.outcomeUnknown) return
      await cancelProjectReads(client, projectId)
      await refreshProject(client, projectId)
    },
  })
}

export function useCreateProject() {
  const client = useQueryClient()
  return useMutation<ProjectResponse, ApiError, CreateProjectRequest>({
    mutationFn: createProject,
    // Fail offline instead of queuing a write to resume without user confirmation.
    networkMode: 'always',
    retry: false,
    onSuccess: (project) => cacheProject(client, project),
    onError: async (error) => {
      if (!error.outcomeUnknown) return
      await cancelProjectReads(client)
      await refreshProject(client)
    },
  })
}

export function expenseQueryOptions(projectId: string | null, filters: ExpenseFilters = {}) {
  return queryOptions<ExpenseResponse[], ApiError>({
    queryKey: queryKeys.expenseList(projectId, filters),
    queryFn: ({ signal }) => getExpenses(projectId, filters, signal),
    staleTime: 30000,
    networkMode: 'always',
    retry: false,
  })
}

export function useExpenses(projectId: string | null = null, enabled = true, filters: ExpenseFilters = {}) {
  return useQuery({ ...expenseQueryOptions(projectId, filters), enabled })
}

export function useRegisterExpense() {
  const client = useQueryClient()
  return useMutation<ExpenseResponse, ApiError, RegisterExpenseRequest>({
    mutationFn: registerExpense,
    networkMode: 'always',
    retry: false,
    onSuccess: (expense) => refreshExpenseAccount(client, expense.project_id ?? null),
    onError: (error, body) => error.outcomeUnknown ? refreshExpenseAccount(client, body.project_id ?? null) : undefined,
  })
}
