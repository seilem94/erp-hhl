import type { ReactNode } from 'react'

type FormFieldProps = {
  id: string
  label: string
  error?: string
  hint?: string
  required?: boolean
  children: ReactNode
}

export function FormField({ id, label, error, hint, required, children }: FormFieldProps) {
  return (
    <div className="min-w-0">
      <label htmlFor={id} className="mb-2 block text-sm font-medium text-brand-navy dark:text-slate-100">
        {label}{required && <span aria-hidden="true" className="ml-1 text-brand-blue dark:text-blue-400">*</span>}
      </label>
      {children}
      {hint && <p id={`${id}-hint`} className="mt-2 text-xs leading-5 text-slate-500 dark:text-slate-400">{hint}</p>}
      {error && <p id={`${id}-error`} className="mt-2 text-sm text-red-700 dark:text-red-300 [overflow-wrap:anywhere]">{error}</p>}
    </div>
  )
}
