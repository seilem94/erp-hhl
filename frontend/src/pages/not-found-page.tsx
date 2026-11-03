import { Link } from '@tanstack/react-router'

export function NotFoundPage() {
  return (
    <section aria-labelledby="not-found-title">
      <h1 id="not-found-title" className="text-3xl font-semibold tracking-tight">
        Página no encontrada
      </h1>
      <p className="mt-4 text-slate-600">La dirección solicitada no está disponible.</p>
      <Link to="/" className="mt-6 inline-block font-medium text-blue-700 underline">
        Volver al inicio
      </Link>
    </section>
  )
}
