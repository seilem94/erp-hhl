import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createProject, getProjects } from '@/api/projects'
import { getExpenses, registerExpense } from '@/api/expenses'
import type { ApiError } from '@/api/client'
import type { CreateProjectRequest, ExpenseResponse, ProjectResponse, RegisterExpenseRequest } from '@/api/types'

export const queryKeys = {
  projects: ['projects'] as const,
  expenses: ['expenses'] as const,
  expenseList: (projectId: string | null) => ['expenses', projectId] as const,
}

export function useProjects() {
  return useQuery<ProjectResponse[], ApiError>({
    queryKey: queryKeys.projects,
    queryFn: ({ signal }) => getProjects(signal),
    staleTime: 30000,
    networkMode: 'always',
    retry: false,
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

export function useExpenses(projectId: string | null = null) {
  return useQuery<ExpenseResponse[], ApiError>({
    queryKey: queryKeys.expenseList(projectId),
    queryFn: ({ signal }) => getExpenses(projectId, signal),
    staleTime: 30000,
    networkMode: 'always',
    retry: false,
  })
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
