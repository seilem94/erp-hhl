import type { ReactNode } from 'react'
import { Spinner } from '@/components/ui/spinner'

type FeedbackProps = { children: ReactNode; tone?: 'error' | 'success' | 'info' }

export function Feedback({ children, tone = 'info' }: FeedbackProps) {
  const styles = {
    error: 'border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200',
    info: 'border-brand-border bg-brand-canvas text-slate-600 dark:text-slate-300',
  }
  return <div role={tone === 'error' ? 'alert' : 'status'} aria-atomic="true" className={`min-w-0 rounded-xl border px-4 py-3 text-sm leading-6 [overflow-wrap:anywhere] ${styles[tone]}`}>{children}</div>
}

export function LoadingState({ children }: { children: ReactNode }) {
  return <Feedback><span className="flex items-center gap-3"><Spinner />{children}</span></Feedback>
}

export function QueryError({ message, onRetry, retrying = false }: { message: string; onRetry: () => void; retrying?: boolean }) {
  return (
    <Feedback tone="error">
      <p>{message}</p>
      <button type="button" onClick={onRetry} disabled={retrying} className="mt-2 inline-flex min-h-11 min-w-11 items-center justify-center gap-2 rounded-md px-3 font-semibold underline disabled:opacity-60">
        {retrying && <Spinner />}
        {retrying ? 'Reintentando…' : 'Reintentar'}
      </button>
    </Feedback>
  )
}
