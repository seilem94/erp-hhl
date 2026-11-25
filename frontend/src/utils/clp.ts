const currency = new Intl.NumberFormat('es-CL', {
  style: 'currency',
  currency: 'CLP',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
})
export const maxClp = 9223372036854775807n

export function isClpAmount(value: unknown): value is string {
  return typeof value === 'string' && /^-?[0-9]+$/.test(value)
}

export function isValidClp(value: string, minimum: 0 | 1) {
  if (!isClpAmount(value)) return false
  const amount = BigInt(value)
  return amount >= BigInt(minimum) && amount <= maxClp
}

export function formatCLP(value: string | bigint) {
  return currency.format(BigInt(value))
}

export function sumClp(values: readonly string[]): string {
  return values.reduce((total, amount) => total + BigInt(amount), 0n).toString()
}
