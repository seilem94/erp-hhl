import { FormField } from '@/components/ui/form-field'
import { formatCLP, isValidClp, maxClp } from '@/utils/clp'

type ClpFieldProps = {
  id: string
  name: string
  label: string
  value: string
  onChange: (value: string) => void
  hint: string
  error?: string
  required?: boolean
  placeholder?: string
}

export function ClpField({ id, name, label, value, onChange, hint, error, required, placeholder }: ClpFieldProps) {
  const minimum = required ? 1 : 0
  const preview = isValidClp(value, minimum) ? formatCLP(value) : null
  const description = [`${id}-hint`, error && `${id}-error`, preview && `${id}-preview`].filter(Boolean).join(' ')

  return (
    <FormField id={id} label={label} required={required} hint={hint} error={error}>
      <input id={id} name={name} type="number" step="1" inputMode="numeric" min={minimum} max={maxClp.toString()}
        value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="form-input"
        required={required} aria-invalid={Boolean(error)} aria-describedby={description} />
      {preview && <p id={`${id}-preview`} className="money-value mt-2 text-sm font-semibold">{preview}</p>}
    </FormField>
  )
}
