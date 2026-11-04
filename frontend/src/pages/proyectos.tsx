import { useState } from 'react'
import { Link } from '@tanstack/react-router'
import { projectStatuses, type ProjectStatus } from '@/api/types'
import { useProjects } from '@/hooks/queries'
import { PageHeading } from '@/components/page-heading'
import { ProjectForm } from '@/components/projects/project-form'
import { Feedback, QueryError } from '@/components/ui/feedback'
import { formatDate, formatMoney, statusLabels } from '@/utils/format'

export function ProjectsPage() {
  const query = useProjects()
  const [status, setStatus] = useState<ProjectStatus | 'all'>('all')
  const projects = query.data?.filter((project) => status === 'all' || project.status === status)

  return (
    <div className="page-container py-10 sm:py-14">
      <PageHeading title="Proyectos y Obras" description="Crea nuevas obras y consulta los proyectos de tu equipo." />
      <div className="grid items-start gap-8 lg:grid-cols-[minmax(0,360px)_minmax(0,1fr)]">
        <ProjectForm />
        <section aria-labelledby="projects-list-title" aria-busy={query.isFetching} className="min-w-0">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
            <h2 id="projects-list-title" className="text-xl font-semibold tracking-tight">Obras registradas{query.isSuccess && <span className="ml-2 text-sm font-normal text-slate-500">({query.data.length})</span>}</h2>
            <div>
              <label htmlFor="project-status" className="sr-only">Filtrar proyectos por estado</label>
              <select id="project-status" className="form-input" value={status} onChange={(event) => setStatus(projectStatuses.find((value) => value === event.target.value) ?? 'all')}>
                <option value="all">Todos los estados</option>
                {projectStatuses.map((value) => <option key={value} value={value}>{statusLabels[value]}</option>)}
              </select>
            </div>
          </div>
          <div className="grid gap-4">
            {query.isPending && <Feedback>Cargando proyectos…</Feedback>}
            {query.isError && <QueryError message={query.error.message} onRetry={() => { void query.refetch() }} retrying={query.isFetching} />}
            {!query.isPending && query.isFetching && <p role="status" className="text-sm text-slate-500">Actualizando proyectos…</p>}
            {query.isSuccess && projects?.length === 0 && <div className="form-panel py-10 text-center"><h3 className="font-semibold">{status === 'all' ? 'Aún no hay obras registradas' : 'No hay obras con este estado'}</h3><p className="mt-2 text-sm text-slate-500">{status === 'all' ? 'Crea tu primer proyecto con el formulario.' : 'Prueba con otro filtro para consultar tus proyectos.'}</p></div>}
            {projects?.map((project) => (
              <article key={project.id} className="rounded-2xl border border-brand-border bg-white p-5 sm:p-6">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1"><h3 className="break-words text-lg font-semibold text-brand-navy"><Link to="/proyectos/$projectId" params={{ projectId: project.id }} className="rounded-sm hover:text-brand-blue hover:underline">{project.name}</Link></h3><p className="mt-1 break-words text-sm text-slate-500">{project.client}</p></div>
                  <span className={`rounded-full px-3 py-1.5 text-xs font-medium ${project.status === 'cancelled' ? 'bg-red-50 text-red-700' : 'bg-brand-tint text-brand-deep-blue'}`}>{statusLabels[project.status]}</span>
                </div>
                <dl className="mt-5 grid grid-cols-1 gap-4 border-t border-brand-border pt-4 text-sm sm:grid-cols-2">
                  <div><dt className="text-slate-500">Presupuesto</dt><dd className="mt-1 font-semibold tabular-nums">{project.budget == null ? 'Sin presupuesto' : formatMoney(project.budget)}</dd></div>
                  <div><dt className="text-slate-500">Inicio</dt><dd className="mt-1 font-medium">{formatDate(project.start_date)}</dd></div>
                </dl>
                <Link to="/proyectos/$projectId" params={{ projectId: project.id }} className="mt-5 inline-flex min-h-10 items-center rounded-md text-sm font-semibold text-brand-blue hover:underline" aria-label={`Ver detalle de ${project.name}`}>Ver detalle de obra →</Link>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
