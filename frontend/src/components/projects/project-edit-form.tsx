import { useRef, useState, type FormEvent } from 'react'
import { projectStatuses, type ProjectResponse, type UpdateProjectRequest } from '@/api/types'
import { useUpdateProject } from '@/hooks/queries'
import { Feedback } from '@/components/ui/feedback'
import { FormField } from '@/components/ui/form-field'
import { focusInvalid, formString } from '@/utils/forms'
import { statusLabels } from '@/utils/format'

type ProjectEditFormProps = {
  project: ProjectResponse
  onClose: () => void
  onUpdated: (project: ProjectResponse) => void
}

export function ProjectEditForm({ project, onClose, onUpdated }: ProjectEditFormProps) {
  const [initial] = useState(project)
  const mutation = useUpdateProject(project.id)
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
    const status = projectStatuses.find((value) => value === formString(data, 'status'))
    const issues: Record<string, string> = {}
    if (!name) issues.name = 'El nombre de la obra no puede quedar vacío.'
    if (!client) issues.client = 'El cliente no puede quedar vacío.'
    if (!status) issues.status = 'Selecciona un estado válido.'
    const budgetInput = event.currentTarget.elements.namedItem('estimated_budget')
    if ((budgetInput instanceof HTMLInputElement && !budgetInput.validity.valid) || (budget && (!Number.isFinite(Number(budget)) || Number(budget) < 0))) {
      issues.estimated_budget = 'Ingresa un presupuesto mayor o igual a cero, con hasta dos decimales.'
    }
    setValidation(issues)
    if (Object.keys(issues).length) {
      focusInvalid(event.currentTarget, issues)
      return
    }
    const body: UpdateProjectRequest = {}
    if (name !== initial.name) body.name = name
    if (client !== initial.client) body.client = client
    if (budget && budget !== initial.budget) body.estimated_budget = budget
    if (status && status !== initial.status) body.status = status
    if (!Object.keys(body).length) {
      setValidation({ _form: 'No hay cambios para guardar.' })
      return
    }
    submitting.current = true
    mutation.mutate(body, {
      onSuccess: onUpdated,
      onSettled: () => { submitting.current = false },
    })
  }

  return (
    <section id="edit-project" aria-labelledby="edit-project-title" className="form-panel mt-6">
      <h2 id="edit-project-title" className="text-xl font-semibold">Editar Proyecto</h2>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Se actualizarán únicamente los campos modificados.</p>
      <form onSubmit={submit} onChange={clearFeedback} noValidate aria-labelledby="edit-project-title" className="mt-6">
        <fieldset disabled={mutation.isPending} className="grid min-w-0 gap-5 sm:grid-cols-2">
          <legend className="sr-only">Actualizar datos de la obra</legend>
          <FormField id="edit-project-name" label="Nombre" error={errors.name}>
            <input id="edit-project-name" name="name" defaultValue={initial.name} className="form-input" autoFocus aria-invalid={Boolean(errors.name)} aria-describedby={errors.name ? 'edit-project-name-error' : undefined} />
          </FormField>
          <FormField id="edit-project-client" label="Cliente" error={errors.client}>
            <input id="edit-project-client" name="client" defaultValue={initial.client} className="form-input" aria-invalid={Boolean(errors.client)} aria-describedby={errors.client ? 'edit-project-client-error' : undefined} />
          </FormField>
          <FormField id="edit-project-budget" label="Presupuesto Estimado" hint="CLP · Deja vacío para conservar el presupuesto actual." error={errors.estimated_budget}>
            <input id="edit-project-budget" name="estimated_budget" type="number" inputMode="decimal" min="0" step="0.01" defaultValue={initial.budget ?? ''} className="form-input" aria-invalid={Boolean(errors.estimated_budget)} aria-describedby={`edit-project-budget-hint${errors.estimated_budget ? ' edit-project-budget-error' : ''}`} />
          </FormField>
          <FormField id="edit-project-status" label="Estado" error={errors.status}>
            <select id="edit-project-status" name="status" defaultValue={initial.status} className="form-input" aria-invalid={Boolean(errors.status)} aria-describedby={errors.status ? 'edit-project-status-error' : undefined}>
              {projectStatuses.map((status) => <option key={status} value={status}>{statusLabels[status]}</option>)}
            </select>
          </FormField>
          <div className="flex flex-wrap gap-3 sm:col-span-2">
            <button type="submit" className="button-primary">{mutation.isPending ? 'Guardando cambios…' : 'Guardar cambios'}</button>
            <button type="button" onClick={onClose} className="button-secondary">Cancelar</button>
          </div>
        </fieldset>
        <div className="mt-4 grid gap-3">
          {validation._form && <Feedback>{validation._form}</Feedback>}
          {mutation.error && <Feedback tone="error">{mutation.error.message}</Feedback>}
        </div>
      </form>
    </section>
  )
}
