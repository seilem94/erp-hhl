import { ApiError, isRecord } from '@/api/client'
import { expenseCategories, projectStatuses, type ExpenseResponse, type ProjectResponse } from '@/api/types'

const optionalString = (value: unknown) => value === undefined || value === null || typeof value === 'string'
const decimalString = (value: unknown) => typeof value === 'string' && /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(value) && Number.isFinite(Number(value))
const calendarDate = (value: unknown) => {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const date = new Date(`${value}T00:00:00Z`)
  return !Number.isNaN(date.getTime()) && date.toISOString().slice(0, 10) === value
}

function isProject(value: unknown): value is ProjectResponse {
  return isRecord(value)
    && typeof value.id === 'string'
    && typeof value.name === 'string'
    && typeof value.client === 'string'
    && projectStatuses.some((status) => status === value.status)
    && calendarDate(value.start_date)
    && typeof value.created_at === 'string'
    && typeof value.updated_at === 'string'
    && optionalString(value.description)
    && (value.end_date === undefined || value.end_date === null || calendarDate(value.end_date))
    && (value.budget === undefined || value.budget === null || decimalString(value.budget))
}

function isExpense(value: unknown): value is ExpenseResponse {
  return isRecord(value)
    && typeof value.id === 'string'
    && decimalString(value.amount)
    && calendarDate(value.date)
    && expenseCategories.some((category) => category === value.category)
    && typeof value.description === 'string'
    && typeof value.has_receipt === 'boolean'
    && typeof value.created_at === 'string'
    && typeof value.updated_at === 'string'
    && optionalString(value.project_id)
    && optionalString(value.receipt_url)
}

export function decodeProject(value: unknown): ProjectResponse {
  if (!isProject(value)) throw new ApiError('El servicio devolvió un proyecto con formato inesperado.', 502)
  return value
}

export function decodeProjects(value: unknown): ProjectResponse[] {
  if (!Array.isArray(value)) throw new ApiError('El servicio devolvió un listado de proyectos con formato inesperado.', 502)
  return value.map(decodeProject)
}

export function decodeExpense(value: unknown): ExpenseResponse {
  if (!isExpense(value)) throw new ApiError('El servicio devolvió un gasto con formato inesperado.', 502)
  return value
}

export function decodeExpenses(value: unknown): ExpenseResponse[] {
  if (!Array.isArray(value)) throw new ApiError('El servicio devolvió un listado de gastos con formato inesperado.', 502)
  return value.map(decodeExpense)
}
