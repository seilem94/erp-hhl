import type { ExpenseCategory, ProjectStatus } from '@/api/types'

export const statusLabels: Record<ProjectStatus, string> = {
  planning: 'Planificación',
  in_progress: 'En ejecución',
  paused: 'Pausada',
  completed: 'Completada',
  cancelled: 'Cancelada',
}

export const categoryLabels: Record<ExpenseCategory, string> = {
  materials: 'Materiales',
  transport: 'Transporte',
  food: 'Alimentación',
  tools: 'Herramientas',
  maintenance: 'Mantenimiento',
  services: 'Servicios',
  other: 'Otros',
}

const money = new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 2 })
const dateFormat = new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' })

export function formatMoney(value: string) {
  return money.format(Number(value))
}

export function formatDate(value: string) {
  // Parse a calendar date locally instead of shifting it through UTC.
  return dateFormat.format(new Date(`${value}T00:00:00`))
}

export function localToday() {
  const date = new Date()
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
