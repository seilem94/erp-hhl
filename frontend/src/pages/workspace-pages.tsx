import { Link } from '@tanstack/react-router'
import { Icon } from '@/components/ui/icon'
import type { ComponentProps } from 'react'

type ModulePageProps = {
  title: string
  description: string
  icon: ComponentProps<typeof Icon>['name']
}

function ModulePage({ title, description, icon }: ModulePageProps) {
  return (
    <section aria-labelledby="module-title" className="page-container py-12 sm:py-20">
      <Link to="/" className="mb-10 inline-flex items-center gap-2 text-sm font-medium text-brand-blue"><Icon name="arrow-right" className="size-4 rotate-180" />Volver al inicio</Link>
      <span className="card-icon bg-brand-tint text-brand-blue"><Icon name={icon} className="size-6" /></span>
      <h1 id="module-title" className="mt-6 text-3xl font-semibold tracking-tight sm:text-4xl">{title}</h1>
      <p className="mt-4 max-w-xl text-base leading-7 text-slate-500">{description}</p>
      <div className="mt-10 max-w-2xl rounded-2xl border border-brand-border bg-white p-6 sm:p-8">
        <p className="text-sm font-semibold">Próximamente en tu espacio de trabajo</p>
        <p className="mt-2 text-sm leading-6 text-slate-500">Estamos preparando este módulo. Por ahora puedes consultar tus obras y gastos desde el panel de inicio.</p>
      </div>
    </section>
  )
}

export function SettingsPage() {
  return <ModulePage title="Configuración" description="Las preferencias de tu equipo y tu espacio de trabajo." icon="settings" />
}
