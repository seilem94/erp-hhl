import type { ExpenseCategory, ProjectStatus } from '@/api/types'
import { sumDecimalAmounts } from '@/utils/decimal'

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
const decimalSeparator = new Intl.NumberFormat('es-CL').formatToParts(1.1).find((part) => part.type === 'decimal')?.value ?? ','
const dateFormat = new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' })

export function formatMoney(value: string) {
  const normalized = sumDecimalAmounts([value])
  const negative = normalized.startsWith('-')
  const [integer, fraction = ''] = normalized.replace(/^-/, '').split('.')
  // Round the decimal string to cents without losing precision through Number.
  let cents = BigInt(integer) * 100n + BigInt((fraction + '00').slice(0, 2))
  if (Number(fraction[2] ?? '0') >= 5) cents += 1n
  const whole = cents / 100n
  const digits = (cents % 100n).toString().padStart(2, '0').replace(/0+$/, '')
  const parts = money.formatToParts(negative ? whole === 0n ? -0 : -whole : whole)
  const lastInteger = parts.findLastIndex((part) => part.type === 'integer')
  return parts.map((part, index) => part.value + (index === lastInteger && digits ? decimalSeparator + digits : '')).join('')
}

export function formatDate(value: string) {
  // Parse a calendar date locally instead of shifting it through UTC.
  return dateFormat.format(new Date(`${value}T00:00:00`))
}

export function localToday() {
  const date = new Date()
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
