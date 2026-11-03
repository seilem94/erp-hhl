import { Link, Outlet } from '@tanstack/react-router'

export function RootLayout() {
  return (
    <div className="min-h-svh bg-slate-50 text-slate-900">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-10 focus:bg-white focus:p-4"
      >
        Saltar al contenido
      </a>
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-5 sm:px-8">
          <Link to="/" aria-label="HHL ERP — Inicio" className="flex items-center gap-3">
            <span className="rounded-lg bg-blue-700 px-3 py-2 font-semibold text-white">
              HHL
            </span>
            <span className="font-semibold tracking-tight">ERP</span>
          </Link>
          <nav aria-label="Navegación principal">
            <Link to="/" className="rounded-md px-3 py-2 text-sm font-medium text-blue-700">
              Inicio
            </Link>
          </nav>
        </div>
      </header>
      <main id="main-content" className="mx-auto max-w-5xl px-5 py-16 sm:px-8 sm:py-24">
        <Outlet />
      </main>
    </div>
  )
}
