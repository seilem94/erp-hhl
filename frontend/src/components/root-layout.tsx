import { Outlet } from '@tanstack/react-router'
import { Navbar } from '@/components/navbar'

export function RootLayout() {
  return (
    <div className="flex min-h-svh flex-col bg-brand-canvas text-brand-navy dark:text-slate-100">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:rounded-md focus:bg-white dark:focus:bg-slate-900 focus:p-4"
      >
        Saltar al contenido
      </a>
      <Navbar />
      <main id="main-content" tabIndex={-1} className="flex-1 outline-none">
        <Outlet />
      </main>
      <footer className="page-container mt-14 flex flex-wrap items-center justify-between gap-2 border-t border-brand-border py-6 text-xs text-slate-500 dark:text-slate-400 sm:mt-20">
        <p><span className="font-semibold text-slate-600 dark:text-slate-300">HHL ERP</span><span className="mx-2 text-slate-300">/</span>Todo bajo control.</p>
        <p>Hecho para el trabajo en terreno.</p>
      </footer>
    </div>
  )
}
