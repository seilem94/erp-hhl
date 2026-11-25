import { useId, useState } from 'react'
import { Link } from '@tanstack/react-router'
import { auditActions, auditEntities, type AuditAction, type AuditEntity, type AuditFilters, type ProjectResponse } from '@/api/types'
import { FormField } from '@/components/ui/form-field'
import { Feedback, LoadingState, QueryError } from '@/components/ui/feedback'
import { useAuditLogs } from '@/hooks/queries'

const pageSize = 25
const localDateTime = new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' })
const actionLabels: Record<AuditAction, string> = {
  CREATE: 'Creación',
  UPDATE: 'Edición',
  DELETE: 'Eliminación',
}
const entityLabels: Record<AuditEntity, string> = { PROYECTO: 'Proyecto', GASTO: 'Gasto' }

type AuditLogListProps = {
  projectId?: string
  projects?: ProjectResponse[]
  projectsLoading?: boolean
}

export function AuditLogList({ projectId, projects = [], projectsLoading = false }: AuditLogListProps) {
  const id = useId()
  const [filters, setFilters] = useState<AuditFilters>({})
  const [offset, setOffset] = useState(0)
  const query = useAuditLogs({ ...filters, proyecto_id: projectId ?? filters.proyecto_id }, pageSize, offset)
  const logs = query.data?.items ?? []

  function changeFilter(changes: AuditFilters) {
    setFilters((previous) => ({ ...previous, ...changes }))
    setOffset(0)
  }

  return (
    <div aria-busy={query.isFetching} className="min-w-0">
      <div className={`mb-5 grid gap-4 ${projectId ? 'sm:grid-cols-2' : 'sm:grid-cols-3'}`} aria-label="Filtrar actividad" role="group">
        {!projectId && (
          <FormField id={`${id}-project`} label="Proyecto">
            <select id={`${id}-project`} className="form-input" value={filters.proyecto_id ?? ''} disabled={projectsLoading}
              onChange={(event) => changeFilter({ proyecto_id: event.target.value || undefined })}>
              <option value="">{projectsLoading ? 'Cargando proyectos…' : 'Todos los proyectos'}</option>
              {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
            </select>
          </FormField>
        )}
        <FormField id={`${id}-entity`} label="Entidad">
          <select id={`${id}-entity`} className="form-input" value={filters.entidad ?? ''}
            onChange={(event) => changeFilter({ entidad: auditEntities.find((entity) => entity === event.target.value) })}>
            <option value="">Todas las entidades</option>
            {auditEntities.map((entity) => <option key={entity} value={entity}>{entityLabels[entity]}</option>)}
          </select>
        </FormField>
        <FormField id={`${id}-action`} label="Acción">
          <select id={`${id}-action`} className="form-input" value={filters.accion ?? ''}
            onChange={(event) => changeFilter({ accion: auditActions.find((action) => action === event.target.value) })}>
            <option value="">Todas las acciones</option>
            {auditActions.map((action) => <option key={action} value={action}>{actionLabels[action]}</option>)}
          </select>
        </FormField>
      </div>

      {query.isPending && <LoadingState>Cargando actividad…</LoadingState>}
      {query.isError && <QueryError message={query.error.message} onRetry={() => { void query.refetch() }} retrying={query.isFetching} />}
      {query.isSuccess && logs.length === 0 && <Feedback>No hay actividad para los filtros seleccionados.</Feedback>}
      {logs.length > 0 && (
        <ol className="divide-y divide-brand-border rounded-xl border border-brand-border bg-white dark:bg-slate-900" aria-label="Bitácora de actividad">
          {logs.map((log) => (
            <li key={log.id} className="min-w-0 px-4 py-4 sm:px-5">
              <div className="flex flex-wrap items-center gap-x-3 gap-y-2 text-xs">
                <span className="rounded-full bg-brand-tint px-2.5 py-1 font-semibold text-brand-deep-blue dark:text-blue-300">{actionLabels[log.accion]}</span>
                <span className="text-slate-500 dark:text-slate-400">{entityLabels[log.entidad]}</span>
                <time dateTime={log.created_at} className="text-slate-500 dark:text-slate-400 sm:ml-auto">{localDateTime.format(new Date(log.created_at))}</time>
              </div>
              <p className="mt-2 text-sm font-medium [overflow-wrap:anywhere]">{log.resumen}</p>
              <p className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm text-slate-500 [overflow-wrap:anywhere] dark:text-slate-400">
                <span>{log.actor_email}</span>
                {log.proyecto_id ? (
                  <Link to="/proyectos/$projectId" params={{ projectId: log.proyecto_id }}
                    className="min-h-11 content-center rounded-sm font-medium text-brand-blue hover:underline dark:text-blue-400">
                    {log.proyecto_nombre ?? 'Proyecto asociado'}
                  </Link>
                ) : <span>Sin proyecto asociado</span>}
              </p>
            </li>
          ))}
        </ol>
      )}
      {(offset > 0 || query.data?.has_more) && (
        <nav aria-label="Paginación de actividad" className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <button type="button" className="button-secondary" disabled={offset === 0 || query.isFetching}
            onClick={() => setOffset(offset - pageSize)}>Anterior</button>
          <span className="text-sm text-slate-500 dark:text-slate-400">Página {offset / pageSize + 1}</span>
          <button type="button" className="button-secondary" disabled={!query.data?.has_more || query.isFetching}
            onClick={() => setOffset(offset + pageSize)}>Siguiente</button>
        </nav>
      )}
    </div>
  )
}
