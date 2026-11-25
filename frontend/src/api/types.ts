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
  status?: ProjectStatus | null
  start_date?: string | null
  end_date?: string | null
}

export interface UpdateProjectRequest {
  name?: string | null
  client?: string | null
  estimated_budget?: DecimalInput | null
  status?: ProjectStatus | null
  description?: string | null
}

export interface ExpenseFilters {
  start_date?: string
  end_date?: string
}

export interface RegisterExpenseRequest {
  amount: DecimalInput
  date: string
  category: ExpenseCategory
  description: string
  project_id?: string | null
  receipt_url?: string | null
}

export interface UpdateExpenseRequest extends Partial<RegisterExpenseRequest> {
  has_receipt?: boolean
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

export const auditActions = ['CREATE', 'UPDATE', 'DELETE'] as const
export type AuditAction = typeof auditActions[number]

export const auditEntities = ['PROYECTO', 'GASTO'] as const
export type AuditEntity = typeof auditEntities[number]

export interface AuditFilters {
  proyecto_id?: string
  entidad?: AuditEntity
  accion?: AuditAction
}

export interface AuditLog {
  id: string
  created_at: string
  actor_email: string
  accion: AuditAction
  entidad: AuditEntity
  entidad_id: string
  proyecto_id: string | null
  proyecto_nombre: string | null
  resumen: string
  detalles: Record<string, Record<string, string | boolean | null> | null> | null
}

export interface AuditLogPage {
  items: AuditLog[]
  has_more: boolean
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
