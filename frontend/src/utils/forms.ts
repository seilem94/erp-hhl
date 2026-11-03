export function formString(data: FormData, name: string) {
  const value = data.get(name)
  return typeof value === 'string' ? value.trim() : ''
}

export function focusInvalid(form: HTMLFormElement, errors: Record<string, string>) {
  const name = Object.keys(errors)[0]
  const field = name ? form.elements.namedItem(name) : null
  if (field instanceof HTMLElement) field.focus()
}
