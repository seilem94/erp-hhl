import { expenseCategories, type ExpenseResponse, type ProjectResponse } from '@/api/types'
import { localToday } from '@/utils/format'
import { formString } from '@/utils/forms'

export function readExpenseFields(data: FormData, projectId: string) {
  const selectedCategory = formString(data, 'category')
  return {
    amount: formString(data, 'amount'),
    date: formString(data, 'date'),
    category: expenseCategories.find((category) => category === selectedCategory),
    description: formString(data, 'description'),
    project_id: projectId || null,
  }
}

export function validateExpenseFields(
  form: HTMLFormElement, values: ReturnType<typeof readExpenseFields>, projects: ProjectResponse[], initial?: ExpenseResponse,
) {
  const { amount, date, category, description, project_id } = values
  const issues: Record<string, string> = {}
  const amountInput = form.elements.namedItem('amount')
  if (amount !== initial?.amount && (!amount || !Number.isFinite(Number(amount)) || Number(amount) <= 0
    || (amountInput instanceof HTMLInputElement && !amountInput.validity.valid))) {
    issues.amount = 'Ingresa un monto entre $0,01 y $9.999.999.999,99, con hasta dos decimales.'
  }
  if (date !== initial?.date) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) issues.date = 'Selecciona una fecha válida.'
    else if (date > localToday()) issues.date = 'La fecha no puede ser futura.'
  }
  if (!category) issues.category = 'Selecciona una categoría.'
  if (!description && description !== initial?.description.trim()) issues.description = 'Describe el gasto.'
  if (project_id && project_id !== initial?.project_id) {
    const project = projects.find((item) => item.id === project_id)
    if (!project) issues.project_id = 'La obra seleccionada no está disponible. Actualiza el listado.'
    else if (project.status === 'cancelled') issues.project_id = 'La obra seleccionada está cancelada.'
  }
  return issues
}
