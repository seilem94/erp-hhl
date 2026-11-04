import { useState } from 'react'
import { PageHeading } from '@/components/page-heading'
import { Feedback } from '@/components/ui/feedback'
import { FormField } from '@/components/ui/form-field'
import { saveTheme, type Theme } from '@/utils/theme'

export function SettingsPage() {
  const [theme, setTheme] = useState<Theme>(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light')
  const [persisted, setPersisted] = useState<boolean | null>(null)

  function changeTheme(theme: Theme) {
    setTheme(theme)
    setPersisted(saveTheme(theme))
  }

  return (
    <div className="page-container py-10 sm:py-14">
      <PageHeading title="Configuración" description="Personaliza la apariencia de tu espacio de trabajo." />
      <div className="grid max-w-4xl items-start gap-6 md:grid-cols-2">
        <section aria-labelledby="appearance-title" className="form-panel">
          <h2 id="appearance-title" className="text-xl font-semibold">Apariencia</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Elige cómo ver el ERP. La preferencia se conserva en este navegador.</p>
          <div className="mt-6">
            <FormField id="theme" label="Tema">
              <select id="theme" className="form-input" value={theme} onChange={(event) => changeTheme(event.target.value === 'dark' ? 'dark' : 'light')}>
                <option value="light">Modo Claro</option>
                <option value="dark">Modo Oscuro</option>
              </select>
            </FormField>
          </div>
          {persisted !== null && <div className="mt-5"><Feedback tone={persisted ? 'success' : 'info'}>{persisted ? 'Preferencia guardada en este navegador.' : 'El tema se aplicó, pero el navegador no permitió guardar la preferencia. Al recargar podría perderse.'}</Feedback></div>}
        </section>
        <section aria-labelledby="about-title" className="form-panel">
          <h2 id="about-title" className="text-xl font-semibold">Acerca de</h2>
          <p className="mt-4 font-semibold text-brand-blue dark:text-blue-400">HHL ERP</p>
          <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Gestión de obras y gastos para tu equipo.</p>
          <dl className="mt-6 border-t border-brand-border pt-5 text-sm"><dt className="text-slate-500 dark:text-slate-400">Versión del ERP</dt><dd className="mt-2 font-semibold">v1.0.0-MVP</dd></dl>
        </section>
      </div>
    </div>
  )
}
