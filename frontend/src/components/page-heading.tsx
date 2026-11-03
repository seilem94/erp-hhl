import { Link } from '@tanstack/react-router'
import { Icon } from '@/components/ui/icon'

export function PageHeading({ title, description }: { title: string; description: string }) {
  return (
    <header className="mb-8 sm:mb-10">
      <Link to="/" className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-brand-blue"><Icon name="arrow-right" className="size-4 rotate-180" />Volver al inicio</Link>
      <h1 className="text-3xl font-semibold tracking-tight text-brand-navy sm:text-4xl">{title}</h1>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500 sm:text-base">{description}</p>
    </header>
  )
}
