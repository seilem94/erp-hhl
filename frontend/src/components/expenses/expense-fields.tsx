import { useId } from 'react'
import { expenseCategories, type ExpenseResponse, type ProjectResponse } from '@/api/types'
import { ClpField } from '@/components/ui/clp-field'
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
  amount: string
  onAmountChange: (amount: string) => void
  initial?: ExpenseResponse
}

export function ExpenseFields({
  idPrefix, errors, projects, projectsLoading, projectsUnavailable,
  projectId, onProjectChange, amount, onAmountChange, initial,
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
      <ClpField id={id('amount')} name="amount" label="Monto" required hint="Pesos chilenos (CLP)." error={errors.amount}
        value={amount} onChange={onAmountChange} placeholder="Ej. 15000" />
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
        <FormField id={id('title')} label="Título" required error={errors.title}>
          <input id={id('title')} name="title" defaultValue={initial?.title}
            placeholder="Ej. Compra cable EVA 2,5 mm" className="form-input"
            required aria-invalid={Boolean(errors.title)} aria-describedby={describedBy('title')} />
        </FormField>
      </div>
      <div className="sm:col-span-2">
        <FormField id={id('detail')} label="Detalle" hint="Opcional." error={errors.detail}>
          <textarea id={id('detail')} name="detail" rows={2} defaultValue={initial?.detail ?? ''}
            className="form-input resize-y" aria-invalid={Boolean(errors.detail)} aria-describedby={describedBy('detail', 'detail', true)} />
        </FormField>
      </div>
    </>
  )
}

export function ExpenseReceiptField({
  checked, onChange, hasDigitalReceipt = false,
}: {
  checked: boolean
  onChange: (checked: boolean) => void
  hasDigitalReceipt?: boolean
}) {
  const hintId = useId()

  return (
    <div className="sm:col-span-2">
      <label className="flex min-h-11 items-center gap-3 text-sm font-medium">
        <input name="has_receipt" type="checkbox" checked={checked || hasDigitalReceipt}
          disabled={hasDigitalReceipt} onChange={(event) => onChange(event.target.checked)}
          aria-describedby={hintId} className="size-4 accent-brand-blue" />
        Tiene comprobante
      </label>
      <p id={hintId} className="text-xs text-slate-500 dark:text-slate-400">
        {hasDigitalReceipt ? 'El enlace indica que el gasto tiene un comprobante.' : 'Marca esta casilla si conservas una boleta o factura.'}
      </p>
    </div>
  )
}
