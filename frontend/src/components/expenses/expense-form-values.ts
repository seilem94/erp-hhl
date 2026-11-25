import { expenseCategories, type ExpenseResponse, type ProjectResponse } from '@/api/types'
import { localToday } from '@/utils/format'
import { formString, validClpField } from '@/utils/forms'

export function readExpenseFields(data: FormData, projectId: string) {
  const selectedCategory = formString(data, 'category')
  return {
    amount: formString(data, 'amount'),
    date: formString(data, 'date'),
    category: expenseCategories.find((category) => category === selectedCategory),
    title: formString(data, 'title'),
    detail: formString(data, 'detail') || null,
    project_id: projectId || null,
  }
}

export function validateExpenseFields(
  form: HTMLFormElement, values: ReturnType<typeof readExpenseFields>, projects: ProjectResponse[], initial?: ExpenseResponse,
) {
  const { amount, date, category, title, project_id } = values
  const issues: Record<string, string> = {}
  if (!validClpField(form, 'amount', amount, 1, initial?.amount)) {
    issues.amount = 'Ingresa un monto entero mayor a cero en pesos chilenos.'
  }
  if (date !== initial?.date) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) issues.date = 'Selecciona una fecha válida.'
    else if (date > localToday()) issues.date = 'La fecha no puede ser futura.'
  }
  if (!category) issues.category = 'Selecciona una categoría.'
  if (!title && title !== initial?.title.trim()) issues.title = 'Ingresa el título del gasto.'
  if (project_id && project_id !== initial?.project_id) {
    const project = projects.find((item) => item.id === project_id)
    if (!project) issues.project_id = 'La obra seleccionada no está disponible. Actualiza el listado.'
    else if (project.status === 'cancelled') issues.project_id = 'La obra seleccionada está cancelada.'
  }
  return issues
}
