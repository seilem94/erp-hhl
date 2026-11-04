import { queryOptions, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createProject, getProjects, updateProject } from '@/api/projects'
import { getExpenses, registerExpense } from '@/api/expenses'
import type { ApiError } from '@/api/client'
import type { CreateProjectRequest, ExpenseFilters, ExpenseResponse, ProjectResponse, RegisterExpenseRequest, UpdateProjectRequest } from '@/api/types'

export const queryKeys = {
  projects: ['projects'] as const,
  project: (projectId: string) => ['projects', 'detail', projectId] as const,
  expenses: ['expenses'] as const,
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
    staleTime: 30000,
    networkMode: 'always',
    retry: false,
  })
}

export function useUpdateProject(projectId: string) {
  const client = useQueryClient()
  return useMutation<ProjectResponse, ApiError, UpdateProjectRequest>({
    mutationFn: (body) => updateProject(projectId, body),
    networkMode: 'always',
    retry: false,
    onSuccess: async (project) => {
      client.setQueryData(queryKeys.project(projectId), project)
      client.setQueryData<ProjectResponse[]>(queryKeys.projects, (projects) => projects?.map((item) => item.id === projectId ? project : item))
      await client.invalidateQueries({ queryKey: queryKeys.projects, exact: true })
      await client.invalidateQueries({ queryKey: queryKeys.project(projectId), exact: true })
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
    onSuccess: () => client.invalidateQueries({ queryKey: queryKeys.projects }),
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
    onSuccess: () => client.invalidateQueries({ queryKey: queryKeys.expenses }),
  })
}
