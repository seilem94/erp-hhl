// DTOs derived from the running API's /openapi.json. Decimal responses are strings.
export const projectStatuses = ['planning', 'in_progress', 'paused', 'completed', 'cancelled'] as const
export type ProjectStatus = typeof projectStatuses[number]

export const expenseCategories = ['materials', 'transport', 'food', 'tools', 'maintenance', 'services', 'other'] as const
export type ExpenseCategory = typeof expenseCategories[number]
export type DecimalInput = string | number

export interface ProjectResponse {
  id: string
  name: string
  client: string
  status: ProjectStatus
  start_date: string
  created_at: string
  updated_at: string
  description?: string | null
  end_date?: string | null
  budget?: string | null
}

export interface CreateProjectRequest {
  name: string
  client: string
  estimated_budget?: DecimalInput | null
  description?: string | null
}

export interface RegisterExpenseRequest {
  amount: DecimalInput
  date: string
  category: ExpenseCategory
  description: string
  project_id?: string | null
  receipt_url?: string | null
}

export interface ExpenseResponse {
  id: string
  amount: string
  date: string
  category: ExpenseCategory
  description: string
  has_receipt: boolean
  created_at: string
  updated_at: string
  project_id?: string | null
  receipt_url?: string | null
}

export interface ErrorResponse {
  detail: string
}

export interface ValidationError {
  loc: (string | number)[]
  msg: string
  type: string
}

export interface HTTPValidationError {
  detail: ValidationError[]
}
