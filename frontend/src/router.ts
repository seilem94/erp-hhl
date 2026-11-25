import { createRootRoute, createRoute, createRouter } from '@tanstack/react-router'
import { RootLayout } from '@/components/root-layout'
import { HomePage } from '@/pages/home-page'
import { NotFoundPage } from '@/pages/not-found-page'
import { SettingsPage } from '@/pages/configuracion'
import { ProjectsPage } from '@/pages/proyectos'
import { ExpensesPage } from '@/pages/gastos'
import { ProjectDetailPage } from '@/pages/proyecto-detalle'
import { AuditPage } from '@/pages/auditoria'

const rootRoute = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFoundPage,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

const projectsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/proyectos', component: ProjectsPage })
const projectDetailRoute = createRoute({ getParentRoute: () => rootRoute, path: '/proyectos/$projectId', component: ProjectDetailPage })
const expensesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/gastos',
  validateSearch: (search: Record<string, unknown>): { vista?: 'registrar' | 'consultar' } => {
    const { vista } = search
    return vista === 'registrar' || vista === 'consultar' ? { vista } : {}
  },
  component: ExpensesPage,
})
const auditRoute = createRoute({ getParentRoute: () => rootRoute, path: '/auditoria', component: AuditPage })
const settingsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/configuracion', component: SettingsPage })

export const router = createRouter({
  routeTree: rootRoute.addChildren([indexRoute, projectsRoute, projectDetailRoute, expensesRoute, auditRoute, settingsRoute]),
  defaultHashScrollIntoView: true,
  scrollRestoration: true,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
