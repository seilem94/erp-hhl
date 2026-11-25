import { useRef, useState } from 'react'
import type { ExpenseResponse } from '@/api/types'
import { ExpenseEditDialog } from '@/components/expenses/expense-edit-dialog'
import { Feedback } from '@/components/ui/feedback'
import { formatCLP } from '@/utils/clp'
import { categoryLabels, formatDate } from '@/utils/format'

export function ExpenseList({ expenses }: { expenses: readonly ExpenseResponse[] }) {
  const [editing, setEditing] = useState<ExpenseResponse | null>(null)
  const [saved, setSaved] = useState(false)
  const editButton = useRef<HTMLButtonElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  function closeEditor() {
    setEditing(null)
    requestAnimationFrame(() => {
      const target = editButton.current?.isConnected ? editButton.current : listRef.current
      target?.focus()
    })
  }

  return (
    <div ref={listRef} tabIndex={-1} className="min-w-0">
      {saved && <Feedback tone="success">Gasto actualizado correctamente.</Feedback>}
      {expenses.length > 0 && (
        <ul className={`grid min-w-0 grid-cols-1 gap-3${saved ? ' mt-3' : ''}`} aria-label="Listado de gastos">
          {expenses.map((expense) => (
            <li key={expense.id} className="min-w-0">
              <article className="rounded-xl border border-brand-border bg-white dark:bg-slate-900 p-5">
                <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
                  <div className="min-w-0 flex-1 basis-40">
                    <h3 className="text-sm font-semibold [overflow-wrap:anywhere]">{expense.title}</h3>
                    {expense.detail?.trim() && (
                      <p className="mt-1 text-xs whitespace-pre-line text-slate-500 [overflow-wrap:anywhere] dark:text-slate-400">{expense.detail}</p>
                    )}
                  </div>
                  <p className="money-value text-sm font-semibold text-brand-navy dark:text-slate-100">{formatCLP(expense.amount)}</p>
                </div>
                <div className="mt-1 flex flex-wrap items-center justify-between gap-x-4">
                  <p className="text-xs text-slate-500 dark:text-slate-400">{categoryLabels[expense.category]} · {formatDate(expense.date)}</p>
                  <button type="button" aria-haspopup="dialog" aria-label={`Editar gasto ${expense.title}`}
                    className="inline-flex min-h-11 items-center rounded-lg px-2 text-sm font-semibold text-brand-blue hover:underline dark:text-blue-400"
                    onClick={(event) => {
                      editButton.current = event.currentTarget
                      setSaved(false)
                      setEditing(expense)
                    }}>Editar</button>
                </div>
              </article>
            </li>
          ))}
        </ul>
      )}
      {editing && <ExpenseEditDialog key={editing.id} expense={editing} onCancel={closeEditor}
        onSaved={() => { setSaved(true); closeEditor() }} />}
    </div>
  )
}
