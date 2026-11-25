import { isValidClp } from '@/utils/clp'

export function formString(data: FormData, name: string) {
  const value = data.get(name)
  return typeof value === 'string' ? value.trim() : ''
}

export function focusInvalid(form: HTMLFormElement, errors: Record<string, string>) {
  const name = Object.keys(errors)[0]
  const field = name ? form.elements.namedItem(name) : null
  if (field instanceof HTMLElement) field.focus()
}

export function validClpField(form: HTMLFormElement, name: string, value: string, minimum: 0 | 1, initial?: string | null) {
  const input = form.elements.namedItem(name)
  if (input instanceof HTMLInputElement && input.validity.badInput) return false
  return value === initial || (minimum === 0 && value === '') || isValidClp(value, minimum)
}
