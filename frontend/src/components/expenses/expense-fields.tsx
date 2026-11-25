import { expenseCategories, type ExpenseResponse, type ProjectResponse } from '@/api/types'
import { FormField } from '@/components/ui/form-field'
import { categoryLabels, localToday } from '@/utils/format'

type ExpenseFieldsProps = {
  idPrefix: string
  errors: Record<string, string>
  projects: ProjectResponse[]
  projectsLoading: boolean
  projectsUnavailable: boolean
  projectId: string
  onProjectChange: (id: string) => void
  initial?: ExpenseResponse
}

export function ExpenseFields({
  idPrefix, errors, projects, projectsLoading, projectsUnavailable,
  projectId, onProjectChange, initial,
}: ExpenseFieldsProps) {
  const today = localToday()
  const id = (field: string) => `${idPrefix}-${field}`
  const describedBy = (field: string, name = field, hasHint = false) => [
    hasHint ? `${id(field)}-hint` : null,
    errors[name] ? `${id(field)}-error` : null,
  ].filter(Boolean).join(' ') || undefined
  const currentProject = initial?.project_id
  const showCurrentProject = currentProject && !projects.some((project) => project.id === currentProject)
  const projectHint = projectsUnavailable
    ? 'No se pudo cargar el listado de obras.'
    : 'Sin proyecto, el gasto se imputa a gastos operativos (OPEX).'

  return (
    <>
      <FormField id={id('amount')} label="Monto" required hint="Pesos chilenos (CLP)." error={errors.amount}>
        <input id={id('amount')} name="amount" type="number" inputMode="decimal" min="0.01" step="0.01"
          max="9999999999.99" defaultValue={initial?.amount} placeholder="Ej. 15000" className="form-input"
          required aria-invalid={Boolean(errors.amount)} aria-describedby={describedBy('amount', 'amount', true)} />
      </FormField>
      <FormField id={id('date')} label="Fecha" required error={errors.date}>
        <input id={id('date')} name="date" type="date" defaultValue={initial?.date ?? today} max={today}
          className="form-input" required aria-invalid={Boolean(errors.date)} aria-describedby={describedBy('date')} />
      </FormField>
      <FormField id={id('category')} label="Categoría" required error={errors.category}>
        <select id={id('category')} name="category" defaultValue={initial?.category ?? ''} className="form-input"
          required aria-invalid={Boolean(errors.category)} aria-describedby={describedBy('category')}>
          <option value="" disabled>Selecciona una categoría</option>
          {expenseCategories.map((category) => <option key={category} value={category}>{categoryLabels[category]}</option>)}
        </select>
      </FormField>
      <FormField id={id('project')} label="Proyecto asociado" hint={projectHint} error={errors.project_id}>
        <select id={id('project')} name="project_id" value={projectId} onChange={(event) => onProjectChange(event.target.value)}
          disabled={projectsLoading || projectsUnavailable} className="form-input"
          aria-invalid={Boolean(errors.project_id)} aria-describedby={describedBy('project', 'project_id', true)}>
          <option value="">{projectsLoading ? 'Cargando proyectos…' : 'Sin proyecto · Gasto operativo'}</option>
          {showCurrentProject && <option value={currentProject}>Proyecto actual</option>}
          {projects.map((project) => (
            <option key={project.id} value={project.id} disabled={project.status === 'cancelled' && project.id !== currentProject}>
              {project.name}{project.status === 'cancelled' ? ' — Cancelada' : ''}
            </option>
          ))}
        </select>
      </FormField>
      <div className="sm:col-span-2">
        <FormField id={id('description')} label="Descripción" required error={errors.description}>
          <textarea id={id('description')} name="description" rows={3} defaultValue={initial?.description}
            placeholder="Ej. Compra de materiales para instalación" className="form-input resize-y"
            required aria-invalid={Boolean(errors.description)} aria-describedby={describedBy('description')} />
        </FormField>
      </div>
    </>
  )
}
