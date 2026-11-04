// Sum API decimal strings exactly before converting anything for presentation.
// This also supports decimal strings in scientific notation.
export function sumDecimalAmounts(values: readonly string[]): string {
  const parts = values.map((value) => {
    const [mantissa, exponent = '0'] = value.trim().toLowerCase().split('e')
    const [whole, fraction = ''] = mantissa.split('.')
    const units = BigInt(`${whole}${fraction}`)
    return { units, scale: units === 0n ? 0 : fraction.length - Number(exponent) }
  })
  const scale = parts.reduce((maximum, part) => Math.max(maximum, part.scale), 0)
  const units = parts.reduce((total, part) => total + part.units * 10n ** BigInt(scale - part.scale), 0n)
  const sign = units < 0n ? '-' : ''
  const digits = (units < 0n ? -units : units).toString().padStart(scale + 1, '0')
  if (scale === 0) return `${sign}${digits}`
  return `${sign}${digits.slice(0, -scale)}.${digits.slice(-scale)}`
}
