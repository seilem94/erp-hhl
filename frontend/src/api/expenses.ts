import { request } from '@/api/client'
import { decodeExpense, decodeExpenses } from '@/api/decoders'
import type { ExpenseFilters, ExpenseResponse, RegisterExpenseRequest } from '@/api/types'

export function registerExpense(body: RegisterExpenseRequest): Promise<ExpenseResponse> {
  return request('/api/v1/expenses/', decodeExpense, { method: 'POST', body })
}

export function getExpenses(projectId: string | null = null, filters: ExpenseFilters = {}, signal?: AbortSignal): Promise<ExpenseResponse[]> {
  const path = projectId
    ? `/api/v1/expenses/project/${encodeURIComponent(projectId)}`
    : '/api/v1/expenses/operational'
  return request(path, decodeExpenses, { signal, queryParams: { start_date: filters.start_date, end_date: filters.end_date } })
}
