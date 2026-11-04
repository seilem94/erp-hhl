import type { ExpenseResponse } from '@/api/types'
import { categoryLabels, formatDate, formatMoney } from '@/utils/format'

export function ExpenseList({ expenses }: { expenses: readonly ExpenseResponse[] }) {
  return (
    <ul className="grid gap-3" aria-label="Listado de gastos">
      {expenses.map((expense) => (
        <li key={expense.id}>
          <article className="rounded-xl border border-brand-border bg-white dark:bg-slate-900 p-5">
            <div className="flex items-start justify-between gap-4">
              <h3 className="min-w-0 break-words text-sm font-semibold">{expense.description}</h3>
              <p className="shrink-0 text-sm font-semibold text-brand-navy dark:text-slate-100 tabular-nums">{formatMoney(expense.amount)}</p>
            </div>
            <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{categoryLabels[expense.category]} · {formatDate(expense.date)}</p>
          </article>
        </li>
      ))}
    </ul>
  )
}
