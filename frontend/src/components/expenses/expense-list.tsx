import type { ExpenseResponse } from '@/api/types'
import { categoryLabels, formatDate, formatMoney } from '@/utils/format'

export function ExpenseList({ expenses }: { expenses: readonly ExpenseResponse[] }) {
  return (
    <ul className="grid min-w-0 grid-cols-1 gap-3" aria-label="Listado de gastos">
      {expenses.map((expense) => (
        <li key={expense.id} className="min-w-0">
          <article className="rounded-xl border border-brand-border bg-white dark:bg-slate-900 p-5">
            <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
              <h3 className="min-w-0 flex-1 basis-40 break-words text-sm font-semibold">{expense.description}</h3>
              <p className="money-value text-sm font-semibold text-brand-navy dark:text-slate-100">{formatMoney(expense.amount)}</p>
            </div>
            <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{categoryLabels[expense.category]} · {formatDate(expense.date)}</p>
          </article>
        </li>
      ))}
    </ul>
  )
}
