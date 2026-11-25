import { AuditLogList } from '@/components/audit/audit-log-list'
import { PageHeading } from '@/components/page-heading'
import { QueryError } from '@/components/ui/feedback'
import { useProjects } from '@/hooks/queries'

export function AuditPage() {
  const projects = useProjects()

  return (
    <div className="page-container py-10 sm:py-14">
      <PageHeading title="Auditoría" description="Consulta quién creó, editó o eliminó proyectos y gastos." />
      <div className="max-w-4xl">
        {projects.isError && (
          <div className="mb-5">
            <QueryError message="No se pudo cargar el listado de proyectos para filtrar la actividad."
              onRetry={() => { void projects.refetch() }} retrying={projects.isFetching} />
          </div>
        )}
        <AuditLogList projects={projects.data} projectsLoading={projects.isPending} />
      </div>
    </div>
  )
}
