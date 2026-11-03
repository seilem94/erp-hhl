import type { ReactNode } from 'react'

type FeedbackProps = { children: ReactNode; tone?: 'error' | 'success' | 'info' }

export function Feedback({ children, tone = 'info' }: FeedbackProps) {
  const styles = {
    error: 'border-red-200 bg-red-50 text-red-800',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
    info: 'border-brand-border bg-brand-canvas text-slate-600',
  }
  return <div role={tone === 'error' ? 'alert' : 'status'} className={`rounded-xl border px-4 py-3 text-sm leading-6 ${styles[tone]}`}>{children}</div>
}

export function QueryError({ message, onRetry, retrying = false }: { message: string; onRetry: () => void; retrying?: boolean }) {
  return (
    <Feedback tone="error">
      <p>{message}</p>
      <button type="button" onClick={onRetry} disabled={retrying} className="mt-2 min-h-10 rounded-md px-2 font-semibold underline disabled:opacity-60">
        {retrying ? 'Reintentando…' : 'Reintentar'}
      </button>
    </Feedback>
  )
}
