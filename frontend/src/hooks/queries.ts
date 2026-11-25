import { queryOptions, useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { getAuditLogs } from '@/api/audit'
import { createProject, getProjects, updateProject } from '@/api/projects'
import { getExpenses, registerExpense, updateExpense } from '@/api/expenses'
import type { ApiError } from '@/api/client'
import type { AuditFilters, AuditLogPage, CreateProjectRequest, ExpenseFilters, ExpenseResponse, ProjectResponse, RegisterExpenseRequest, UpdateExpenseRequest, UpdateProjectRequest } from '@/api/types'

export const queryKeys = {
  projects: ['projects'] as const,
  project: (projectId: string) => ['projects', 'detail', projectId] as const,
  expenses: ['expenses'] as const,
  expenseAccount: (projectId: string | null) => ['expenses', projectId] as const,
  expenseList: (projectId: string | null, filters: ExpenseFilters = {}) => ['expenses', projectId, { start_date: filters.start_date || null, end_date: filters.end_date || null }] as const,
  audit: ['audit'] as const,
  auditPage: (filters: AuditFilters, limit: number, offset: number) => ['audit', filters, limit, offset] as const,
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

async function refreshAudit(client: QueryClient) {
  await client.cancelQueries({ queryKey: queryKeys.audit })
  await client.invalidateQueries({ queryKey: queryKeys.audit })
}

async function refreshExpensesAndAudit(client: QueryClient, ...accounts: (string | null)[]) {
  await Promise.all([
    refreshAudit(client),
    ...[...new Set(accounts)].map((account) => refreshExpenseAccount(client, account)),
  ])
}

export function useUpdateProject(projectId: string) {
  const client = useQueryClient()
  return useMutation<ProjectResponse, ApiError, UpdateProjectRequest>({
    mutationFn: (body) => updateProject(projectId, body),
    networkMode: 'always',
    retry: false,
    onSuccess: (project) => Promise.all([cacheProject(client, project), refreshAudit(client)]),
    onError: async (error) => {
      if (!error.outcomeUnknown) return
      await cancelProjectReads(client, projectId)
      await Promise.all([refreshProject(client, projectId), refreshAudit(client)])
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
    onSuccess: (project) => Promise.all([cacheProject(client, project), refreshAudit(client)]),
    onError: async (error) => {
      if (!error.outcomeUnknown) return
      await cancelProjectReads(client)
      await Promise.all([refreshProject(client), refreshAudit(client)])
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
    onSuccess: (expense) => refreshExpensesAndAudit(client, expense.project_id ?? null),
    onError: (error, body) => error.outcomeUnknown ? refreshExpensesAndAudit(client, body.project_id ?? null) : undefined,
  })
}

export function useUpdateExpense(expense: ExpenseResponse) {
  const client = useQueryClient()
  const source = expense.project_id ?? null
  return useMutation<ExpenseResponse, ApiError, UpdateExpenseRequest>({
    mutationFn: (body) => updateExpense(expense.id, body),
    networkMode: 'always',
    retry: false,
    onSuccess: (updated) => refreshExpensesAndAudit(client, source, updated.project_id ?? null),
    onError: (error, body) => error.outcomeUnknown
      ? refreshExpensesAndAudit(client, source, body.project_id === undefined ? source : body.project_id)
      : undefined,
  })
}

export function useAuditLogs(filters: AuditFilters, limit: number, offset: number) {
  return useQuery<AuditLogPage, ApiError>({
    queryKey: queryKeys.auditPage(filters, limit, offset),
    queryFn: ({ signal }) => getAuditLogs(filters, limit, offset, signal),
    staleTime: 30000,
    networkMode: 'always',
    retry: false,
  })
}
