import { useRef, useState, type FormEvent } from 'react'
import type { ExpenseResponse, ProjectResponse } from '@/api/types'
import { useRegisterExpense } from '@/hooks/queries'
import { ExpenseFields } from '@/components/expenses/expense-fields'
import { readExpenseFields, validateExpenseFields } from '@/components/expenses/expense-form-values'
import { Feedback } from '@/components/ui/feedback'
import { Spinner } from '@/components/ui/spinner'
import { Icon } from '@/components/ui/icon'
import { formatMoney, localToday } from '@/utils/format'
import { focusInvalid } from '@/utils/forms'

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
    const values = readExpenseFields(new FormData(event.currentTarget), projectId)
    const issues = validateExpenseFields(event.currentTarget, values, projects)
    setValidation(issues)
    if (Object.keys(issues).length || !values.category) {
      focusInvalid(event.currentTarget, issues)
      return
    }
    submitting.current = true
    mutation.mutate({ ...values, category: values.category }, {
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
    <section id="seccion-registrar-gasto" className="form-panel scroll-mt-4" aria-labelledby="register-expense-title">
      <div className="flex items-center gap-4"><span className="card-icon bg-brand-tint text-brand-blue dark:text-blue-400"><Icon name="receipt" className="size-6" /></span><div><h2 id="register-expense-title" className="text-xl font-semibold tracking-tight">Registro Rápido de Gastos</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Completa los datos de tu compra.</p></div></div>
      <form ref={formRef} onSubmit={submit} onChange={clearFeedback} noValidate aria-busy={mutation.isPending} aria-labelledby="register-expense-title" className="mt-7">
        <fieldset disabled={mutation.isPending} className="grid min-w-0 gap-5 sm:grid-cols-2">
          <legend className="sr-only">Datos del gasto</legend>
          <ExpenseFields idPrefix="expense" errors={errors} projects={projects} projectsLoading={projectsLoading}
            projectsUnavailable={projectsUnavailable} projectId={projectId} onProjectChange={setProjectId} />
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
