import { createRootRoute, createRoute, createRouter } from '@tanstack/react-router'
import { RootLayout } from '@/components/root-layout'
import { HomePage } from '@/pages/home-page'
import { NotFoundPage } from '@/pages/not-found-page'

const rootRoute = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFoundPage,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

export const router = createRouter({
  routeTree: rootRoute.addChildren([indexRoute]),
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
