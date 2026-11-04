import { useRef, useState, type FormEvent } from 'react'
import { expenseCategories, type ExpenseResponse, type ProjectResponse } from '@/api/types'
import { useRegisterExpense } from '@/hooks/queries'
import { Feedback } from '@/components/ui/feedback'
import { Spinner } from '@/components/ui/spinner'
import { FormField } from '@/components/ui/form-field'
import { Icon } from '@/components/ui/icon'
import { categoryLabels, formatMoney, localToday } from '@/utils/format'
import { focusInvalid, formString } from '@/utils/forms'

type ExpenseFormProps = {
  projects: ProjectResponse[]
  projectsLoading: boolean
  projectsUnavailable: boolean
  onRegistered: (expense: ExpenseResponse) => void
}

export function ExpenseForm({ projects, projectsLoading, projectsUnavailable, onRegistered }: ExpenseFormProps) {
  const mutation = useRegisterExpense()
  const formRef = useRef<HTMLFormElement>(null)
  const submitting = useRef(false)
  const [projectId, setProjectId] = useState('')
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
    const amount = formString(data, 'amount')
    const date = formString(data, 'date')
    const category = expenseCategories.find((value) => value === formString(data, 'category'))
    const description = formString(data, 'description')
    const issues: Record<string, string> = {}
    const amountInput = event.currentTarget.elements.namedItem('amount')
    if (!amount || !Number.isFinite(Number(amount)) || Number(amount) <= 0 || (amountInput instanceof HTMLInputElement && !amountInput.validity.valid)) {
      issues.amount = 'Ingresa un monto mayor a cero, con hasta dos decimales.'
    }
    if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) issues.date = 'Selecciona una fecha válida.'
    else if (date > localToday()) issues.date = 'La fecha no puede ser futura.'
    if (!category) issues.category = 'Selecciona una categoría.'
    if (!description) issues.description = 'Describe el gasto.'
    const selected = projects.find((project) => project.id === projectId)
    if (projectId && !selected) issues.project_id = 'La obra seleccionada no está disponible. Actualiza el listado.'
    else if (selected?.status === 'cancelled') issues.project_id = 'No se pueden registrar gastos en una obra cancelada.'
    setValidation(issues)
    if (Object.keys(issues).length || !category) {
      focusInvalid(event.currentTarget, issues)
      return
    }
    submitting.current = true
    mutation.mutate({ amount, date, category, description, project_id: projectId || null }, {
      onSuccess: (expense) => {
        formRef.current?.reset()
        const dateInput = formRef.current?.querySelector<HTMLInputElement>('[name="date"]')
        if (dateInput) dateInput.value = localToday()
        setProjectId('')
        onRegistered(expense)
      },
      onSettled: () => { submitting.current = false },
    })
  }

  return (
    <section className="form-panel" aria-labelledby="register-expense-title">
      <div className="flex items-center gap-4"><span className="card-icon bg-brand-tint text-brand-blue dark:text-blue-400"><Icon name="receipt" className="size-6" /></span><div><h2 id="register-expense-title" className="text-xl font-semibold tracking-tight">Registro Rápido de Gastos</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Completa los datos de tu compra.</p></div></div>
      <form ref={formRef} onSubmit={submit} onChange={clearFeedback} noValidate aria-busy={mutation.isPending} aria-labelledby="register-expense-title" className="mt-7">
        <fieldset disabled={mutation.isPending} className="grid min-w-0 gap-5 sm:grid-cols-2">
          <legend className="sr-only">Datos del gasto</legend>
          <FormField id="expense-amount" label="Monto" required hint="Pesos chilenos (CLP)." error={errors.amount}>
            <input id="expense-amount" name="amount" type="number" inputMode="decimal" min="0.01" step="0.01" placeholder="Ej. 15000" className="form-input" required aria-invalid={Boolean(errors.amount)} aria-describedby={`expense-amount-hint${errors.amount ? ' expense-amount-error' : ''}`} />
          </FormField>
          <FormField id="expense-date" label="Fecha" required error={errors.date}>
            <input id="expense-date" name="date" type="date" defaultValue={localToday()} max={localToday()} className="form-input" required aria-invalid={Boolean(errors.date)} aria-describedby={errors.date ? 'expense-date-error' : undefined} />
          </FormField>
          <FormField id="expense-category" label="Categoría" required error={errors.category}>
            <select id="expense-category" name="category" defaultValue="" className="form-input" required aria-invalid={Boolean(errors.category)} aria-describedby={errors.category ? 'expense-category-error' : undefined}>
              <option value="" disabled>Selecciona una categoría</option>
              {expenseCategories.map((category) => <option key={category} value={category}>{categoryLabels[category]}</option>)}
            </select>
          </FormField>
          <FormField id="expense-project" label="Proyecto Asociado" hint="Sin proyecto, se registra como gasto operativo (OPEX)." error={errors.project_id}>
            <select id="expense-project" name="project_id" value={projectId} onChange={(event) => setProjectId(event.target.value)} disabled={projectsLoading || projectsUnavailable} className="form-input" aria-invalid={Boolean(errors.project_id)} aria-describedby={`expense-project-hint${errors.project_id ? ' expense-project-error' : ''}`}>
              <option value="">{projectsLoading ? 'Cargando proyectos…' : 'Sin proyecto · Gasto operativo'}</option>
              {projects.map((project) => <option key={project.id} value={project.id} disabled={project.status === 'cancelled'}>{project.name}{project.status === 'cancelled' ? ' — Cancelada' : ''}</option>)}
            </select>
          </FormField>
          <div className="sm:col-span-2"><FormField id="expense-description" label="Descripción" required error={errors.description}>
            <textarea id="expense-description" name="description" rows={3} placeholder="Ej. Compra de materiales para instalación" className="form-input resize-y" required aria-invalid={Boolean(errors.description)} aria-describedby={errors.description ? 'expense-description-error' : undefined} />
          </FormField></div>
          <button type="submit" className="button-primary mt-1 sm:col-span-2">{mutation.isPending ? <Spinner /> : <Icon name="plus" className="size-4" />}{mutation.isPending ? 'Registrando gasto…' : 'Registrar Gasto'}</button>
        </fieldset>
        <div className="mt-4 grid gap-3">
          {mutation.error && <Feedback tone="error">{mutation.error.message}</Feedback>}
          {mutation.isSuccess && <Feedback tone="success">Gasto de {formatMoney(mutation.data.amount)} registrado correctamente.</Feedback>}
        </div>
      </form>
    </section>
  )
}
