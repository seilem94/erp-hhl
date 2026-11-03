import { createRootRoute, createRoute, createRouter } from '@tanstack/react-router'
import { RootLayout } from '@/components/root-layout'
import { HomePage } from '@/pages/home-page'
import { NotFoundPage } from '@/pages/not-found-page'
import { ExpensesPage, ProjectsPage, SettingsPage } from '@/pages/workspace-pages'

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
const expensesRoute = createRoute({ getParentRoute: () => rootRoute, path: '/gastos', component: ExpensesPage })
const settingsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/configuracion', component: SettingsPage })

export const router = createRouter({
  routeTree: rootRoute.addChildren([indexRoute, projectsRoute, expensesRoute, settingsRoute]),
  defaultHashScrollIntoView: true,
  scrollRestoration: true,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
