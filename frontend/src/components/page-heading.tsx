import { Link } from '@tanstack/react-router'
import { Icon } from '@/components/ui/icon'

type PageHeadingProps = {
  title: string
  description: string
  backTo?: '/' | '/proyectos'
  backLabel?: string
}

export function PageHeading({ title, description, backTo = '/', backLabel = 'Volver al inicio' }: PageHeadingProps) {
  return (
    <header className="mb-8 sm:mb-10">
      <Link to={backTo} className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-brand-blue dark:text-blue-400"><Icon name="arrow-right" className="size-4 rotate-180" />{backLabel}</Link>
      <h1 className="break-words text-3xl font-semibold tracking-tight text-brand-navy dark:text-slate-100 sm:text-4xl">{title}</h1>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-500 dark:text-slate-400 sm:text-base">{description}</p>
    </header>
  )
}
