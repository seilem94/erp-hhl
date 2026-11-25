import { useRef, useState, type FormEvent } from 'react'
import { projectStatuses } from '@/api/types'
import { useCreateProject } from '@/hooks/queries'
import { Feedback } from '@/components/ui/feedback'
import { Spinner } from '@/components/ui/spinner'
import { FormField } from '@/components/ui/form-field'
import { Icon } from '@/components/ui/icon'
import { focusInvalid, formString } from '@/utils/forms'
import { statusLabels } from '@/utils/format'

const dateFields = [
  { name: 'start_date', label: 'Fecha de inicio' },
  { name: 'end_date', label: 'Fecha de entrega' },
] as const

export function ProjectForm() {
  const mutation = useCreateProject()
  const formRef = useRef<HTMLFormElement>(null)
  const detailsRef = useRef<HTMLDetailsElement>(null)
  const submitting = useRef(false)
  const [validation, setValidation] = useState<Record<string, string>>({})
  const errors = { ...validation, ...mutation.error?.fieldErrors }

  function clearFeedback() {
    if (!mutation.isPending) {
      mutation.reset()
      setValidation({})
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting.current) return
    mutation.reset()
    const data = new FormData(event.currentTarget)
    const name = formString(data, 'name')
    const client = formString(data, 'client')
    const budget = formString(data, 'estimated_budget')
    const initialStatus = formString(data, 'status')
    const issues: Record<string, string> = {}
    if (!name) issues.name = 'Ingresa el nombre de la obra.'
    if (!client) issues.client = 'Ingresa el nombre del cliente.'
    const budgetInput = event.currentTarget.elements.namedItem('estimated_budget')
    if ((budgetInput instanceof HTMLInputElement && !budgetInput.validity.valid) || (budget && (!Number.isFinite(Number(budget)) || Number(budget) < 0))) {
      issues.estimated_budget = 'Ingresa un presupuesto mayor o igual a cero, con hasta dos decimales.'
    }
    for (const { name } of dateFields) {
      const input = event.currentTarget.elements.namedItem(name)
      if (input instanceof HTMLInputElement && !input.validity.valid) {
        issues[name] = 'Ingresa una fecha válida.'
        if (detailsRef.current) detailsRef.current.open = true
      }
    }
    setValidation(issues)
    if (Object.keys(issues).length) {
      focusInvalid(event.currentTarget, issues)
      return
    }
    submitting.current = true
    mutation.mutate({
      name,
      client,
      estimated_budget: budget || undefined,
      description: formString(data, 'description') || undefined,
      status: projectStatuses.find((value) => value === initialStatus),
      start_date: formString(data, 'start_date') || undefined,
      end_date: formString(data, 'end_date') || undefined,
    }, {
      onSuccess: () => {
        formRef.current?.reset()
        if (detailsRef.current) detailsRef.current.open = false
      },
      onError: ({ fieldErrors }) => {
        if (detailsRef.current && (fieldErrors.description || fieldErrors.status || dateFields.some(({ name }) => fieldErrors[name]))) {
          detailsRef.current.open = true
        }
      },
      onSettled: () => { submitting.current = false },
    })
  }

  return (
    <section className="form-panel self-start" aria-labelledby="create-project-title">
      <span className="card-icon bg-brand-tint text-brand-blue dark:text-blue-400"><Icon name="blueprint" className="size-6" /></span>
      <h2 id="create-project-title" className="mt-5 text-xl font-semibold tracking-tight">Nueva obra</h2>
      <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Registra el proyecto y su presupuesto inicial.</p>
      <form ref={formRef} onSubmit={submit} onChange={clearFeedback} noValidate aria-busy={mutation.isPending} aria-labelledby="create-project-title" className="mt-6">
        <fieldset disabled={mutation.isPending} className="grid min-w-0 gap-5">
          <legend className="sr-only">Datos del nuevo proyecto</legend>
          <FormField id="project-name" label="Nombre" required error={errors.name}>
            <input id="project-name" name="name" className="form-input" placeholder="Ej. Instalación eléctrica local" required aria-invalid={Boolean(errors.name)} aria-describedby={errors.name ? 'project-name-error' : undefined} />
          </FormField>
          <FormField id="project-client" label="Cliente" required error={errors.client}>
            <input id="project-client" name="client" className="form-input" placeholder="Nombre o razón social" required aria-invalid={Boolean(errors.client)} aria-describedby={errors.client ? 'project-client-error' : undefined} />
          </FormField>
          <FormField id="project-budget" label="Presupuesto Estimado" hint="Opcional · Pesos chilenos (CLP)." error={errors.estimated_budget}>
            <input id="project-budget" name="estimated_budget" type="number" inputMode="decimal" min="0" step="0.01" className="form-input" placeholder="Ej. 2500000" aria-invalid={Boolean(errors.estimated_budget)} aria-describedby={`project-budget-hint${errors.estimated_budget ? ' project-budget-error' : ''}`} />
          </FormField>
          <details ref={detailsRef} className="group min-w-0 rounded-xl border border-brand-border">
            <summary className="flex min-h-11 cursor-pointer items-center rounded-xl px-3.5 py-2 text-sm font-semibold text-brand-blue hover:underline dark:text-blue-400">
              <span className="group-open:hidden">+ Más detalles (opcional)</span>
              <span className="hidden group-open:inline">- Ocultar detalles</span>
            </summary>
            <div className="grid gap-5 px-3.5 pt-1 pb-4">
              <FormField id="project-description" label="Descripción" hint="Opcional." error={errors.description}>
                <textarea id="project-description" name="description" rows={3} className="form-input resize-y" aria-invalid={Boolean(errors.description)} aria-describedby={`project-description-hint${errors.description ? ' project-description-error' : ''}`} />
              </FormField>
              <FormField id="project-initial-status" label="Estado inicial" hint="Opcional · Planificación por defecto." error={errors.status}>
                <select id="project-initial-status" name="status" className="form-input" aria-invalid={Boolean(errors.status)} aria-describedby={`project-initial-status-hint${errors.status ? ' project-initial-status-error' : ''}`}>
                  <option value="">Selecciona un estado</option>
                  {projectStatuses.map((status) => <option key={status} value={status}>{statusLabels[status]}</option>)}
                </select>
              </FormField>
              {dateFields.map(({ name, label }) => {
                const id = `project-${name}`
                return (
                  <FormField key={name} id={id} label={label} hint="Opcional." error={errors[name]}>
                    <input id={id} name={name} type="date" min="0001-01-01" max="9999-12-31" className="form-input" aria-invalid={Boolean(errors[name])} aria-describedby={`${id}-hint${errors[name] ? ` ${id}-error` : ''}`} />
                  </FormField>
                )
              })}
            </div>
          </details>
          <button type="submit" className="button-primary mt-1">
            {mutation.isPending ? <Spinner /> : <Icon name="plus" className="size-4" />}{mutation.isPending ? 'Guardando obra…' : 'Crear Proyecto'}
          </button>
        </fieldset>
        <div className="mt-4 grid gap-3">
          {mutation.error && <Feedback tone="error">{mutation.error.message}</Feedback>}
          {mutation.isSuccess && <Feedback tone="success">Proyecto «{mutation.data.name}» creado correctamente.</Feedback>}
        </div>
      </form>
    </section>
  )
}
