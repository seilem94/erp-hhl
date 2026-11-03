import { useState } from 'react'
import { Link } from '@tanstack/react-router'
import { Icon } from '@/components/ui/icon'

const navigation = [
  { to: '/', label: 'Inicio' },
  { to: '/proyectos', label: 'Proyectos' },
  { to: '/gastos', label: 'Gastos' },
  { to: '/configuracion', label: 'Configuración' },
] as const

function UserMenu() {
  return (
    <details className="user-menu group relative" onBlur={(event) => {
      if (!event.currentTarget.contains(event.relatedTarget)) event.currentTarget.open = false
    }} onKeyDown={(event) => {
      if (event.key === 'Escape') {
        event.currentTarget.open = false
        event.currentTarget.querySelector('summary')?.focus()
      }
    }}>
      <summary className="flex cursor-pointer list-none items-center gap-2 rounded-full p-1" aria-label="Abrir menú de usuario">
        <span className="flex size-10 items-center justify-center rounded-full border border-brand-border bg-brand-canvas text-brand-navy">
          <Icon name="user" className="size-5" />
        </span>
        <Icon name="chevron-down" className="hidden size-3.5 text-slate-500 transition-transform group-open:rotate-180 sm:block" />
      </summary>
      <div className="absolute right-0 top-full z-30 mt-3 w-60 rounded-2xl border border-brand-border bg-white p-2 shadow-xl shadow-brand-navy/10">
        <p className="px-3 pt-3 text-sm font-semibold">Espacio de trabajo HHL</p>
        <p className="mb-2 border-b border-brand-border px-3 pb-3 pt-1 text-xs text-slate-500">Gestión de obras y gastos</p>
        <Link to="/configuracion" onClick={(event) => event.currentTarget.closest('details')?.removeAttribute('open')} className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm text-slate-600 hover:bg-brand-canvas hover:text-brand-blue">
          <Icon name="settings" className="size-4" /> Configuración
        </Link>
      </div>
    </details>
  )
}

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <header className="relative z-20 border-b border-brand-border bg-white">
      <div className="page-container flex h-22 items-center justify-between gap-6">
        <Link to="/" aria-label="HHL ERP — Inicio" className="flex shrink-0 items-center gap-3" onClick={() => setMobileOpen(false)}>
          <img src="/logo.svg" alt="" width="44" height="44" className="size-11" />
          <span className="text-xl font-semibold tracking-tight">HHL <span className="font-normal text-slate-500">ERP</span></span>
        </Link>
        <div className="flex items-center gap-4 lg:gap-10">
          <nav aria-label="Navegación principal" className="hidden items-center gap-1 lg:flex">
            {navigation.map(({ to, label }) => (
              <Link key={to} to={to} activeOptions={{ exact: true }} className="nav-link" activeProps={{ className: 'bg-brand-tint text-brand-blue' }} inactiveProps={{ className: 'text-slate-500 hover:bg-brand-canvas hover:text-brand-navy' }}>
                {label}
              </Link>
            ))}
          </nav>
          <div className="hidden h-7 w-px bg-brand-border lg:block" />
          <UserMenu />
          <button type="button" className="rounded-lg p-2 text-brand-navy hover:bg-brand-canvas lg:hidden" aria-expanded={mobileOpen} aria-controls="mobile-navigation" aria-label={mobileOpen ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'} onClick={() => setMobileOpen(!mobileOpen)}>
            <Icon name={mobileOpen ? 'close' : 'menu'} className="size-6" />
          </button>
        </div>
      </div>
      <nav id="mobile-navigation" aria-label="Navegación móvil" hidden={!mobileOpen} className="border-t border-brand-border bg-white lg:hidden">
        <div className="page-container grid gap-1 py-3">
          {navigation.map(({ to, label }) => (
            <Link key={to} to={to} activeOptions={{ exact: true }} className="nav-link" activeProps={{ className: 'bg-brand-tint text-brand-blue' }} inactiveProps={{ className: 'text-slate-500' }} onClick={() => setMobileOpen(false)}>
              {label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  )
}
