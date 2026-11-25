import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { ExpenseResponse, UpdateExpenseRequest } from '@/api/types'
import { ExpenseFields, ExpenseReceiptField } from '@/components/expenses/expense-fields'
import { readExpenseFields, validateExpenseFields } from '@/components/expenses/expense-form-values'
import { Feedback } from '@/components/ui/feedback'
import { FormField } from '@/components/ui/form-field'
import { Spinner } from '@/components/ui/spinner'
import { useProjects, useUpdateExpense } from '@/hooks/queries'
import { focusInvalid, formString } from '@/utils/forms'

type ExpenseEditDialogProps = {
  expense: ExpenseResponse
  onCancel: () => void
  onSaved: () => void
}

export function ExpenseEditDialog({ expense, onCancel, onSaved }: ExpenseEditDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const submitting = useRef(false)
  const [projectId, setProjectId] = useState(expense.project_id ?? '')
  const [amount, setAmount] = useState(expense.amount)
  const [hasReceipt, setHasReceipt] = useState(expense.has_receipt)
  const [receiptUrl, setReceiptUrl] = useState(expense.receipt_url ?? '')
  const [validation, setValidation] = useState<Record<string, string>>({})
  const projects = useProjects()
  const mutation = useUpdateExpense(expense)
  const errors = { ...validation, ...mutation.error?.fieldErrors }
  const hasDigitalReceipt = Boolean(receiptUrl.trim())

  useEffect(() => {
    const dialog = dialogRef.current
    dialog?.showModal()
    return () => dialog?.close()
  }, [])

  function clearFeedback() {
    if (!submitting.current) {
      mutation.reset()
      setValidation({})
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting.current) return
    mutation.reset()
    const data = new FormData(event.currentTarget)
    const values = readExpenseFields(data, projectId)
    const issues = validateExpenseFields(event.currentTarget, values, projects.data ?? [], expense)
    setValidation(issues)
    if (Object.keys(issues).length || !values.category) {
      focusInvalid(event.currentTarget, issues)
      return
    }

    const body: UpdateExpenseRequest = {}
    if (values.amount !== expense.amount) body.amount = values.amount
    if (values.date !== expense.date) body.date = values.date
    if (values.category !== expense.category) body.category = values.category
    if (values.title !== expense.title.trim()) body.title = values.title
    if (values.detail !== (expense.detail?.trim() || null)) body.detail = values.detail
    if (values.project_id !== (expense.project_id ?? null)) body.project_id = values.project_id
    const url = formString(data, 'receipt_url') || null
    if (url !== (expense.receipt_url?.trim() || null)) body.receipt_url = url
    const receipt = Boolean(url) || hasReceipt
    if (receipt !== expense.has_receipt) body.has_receipt = receipt
    if (!Object.keys(body).length) {
      setValidation({ _form: 'No hay cambios para guardar.' })
      return
    }

    submitting.current = true
    mutation.mutate(body, {
      onSuccess: onSaved,
      onSettled: () => { submitting.current = false },
    })
  }

  return (
    <dialog ref={dialogRef} aria-labelledby="edit-expense-dialog-title"
      onCancel={(event) => {
        event.preventDefault()
        if (!submitting.current) onCancel()
      }}
      className="form-panel m-auto max-h-[90dvh] w-full max-w-[calc(100%_-_2rem)] overflow-y-auto overscroll-contain backdrop:bg-slate-950/50 sm:max-w-xl">
      <h2 id="edit-expense-dialog-title" className="text-xl font-semibold tracking-tight">Editar gasto</h2>
      <form onSubmit={submit} onChange={clearFeedback} noValidate aria-busy={mutation.isPending} className="mt-5">
        <fieldset disabled={mutation.isPending} className="grid min-w-0 gap-4 sm:grid-cols-2">
          <legend className="sr-only">Datos del gasto</legend>
          <ExpenseFields idPrefix="edit-expense" initial={expense} errors={errors} projects={projects.data ?? []}
            projectsLoading={projects.isPending} projectsUnavailable={projects.isError && !projects.data}
            projectId={projectId} onProjectChange={setProjectId} amount={amount} onAmountChange={setAmount} />
          <div className="sm:col-span-2">
            <FormField id="edit-expense-receipt" label="Enlace o ruta del comprobante" hint="Opcional." error={errors.receipt_url}>
              <input id="edit-expense-receipt" name="receipt_url" type="text" inputMode="url" value={receiptUrl}
                onChange={(event) => setReceiptUrl(event.target.value)} className="form-input"
                aria-invalid={Boolean(errors.receipt_url)} aria-describedby={`edit-expense-receipt-hint${errors.receipt_url ? ' edit-expense-receipt-error' : ''}`} />
            </FormField>
          </div>
          <ExpenseReceiptField checked={hasReceipt} onChange={setHasReceipt} hasDigitalReceipt={hasDigitalReceipt} />
          <div className="flex flex-wrap gap-3 sm:col-span-2">
            <button type="submit" className="button-primary">
              {mutation.isPending && <Spinner />}{mutation.isPending ? 'Guardando…' : 'Guardar cambios'}
            </button>
            <button type="button" className="button-secondary" onClick={onCancel}>Cancelar</button>
          </div>
        </fieldset>
        {mutation.error && <div className="mt-4"><Feedback tone="error">{mutation.error.message}</Feedback></div>}
        {validation._form && <div className="mt-4"><Feedback>{validation._form}</Feedback></div>}
      </form>
    </dialog>
  )
}
