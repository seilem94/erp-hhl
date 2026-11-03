export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL?.trim() || 'http://localhost:8000').replace(/\/+$/, '')

export class ApiError extends Error {
  readonly status: number
  readonly fieldErrors: Record<string, string>

  constructor(message: string, status = 0, fieldErrors: Record<string, string> = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.fieldErrors = fieldErrors
  }
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function responseError(status: number, payload: unknown): ApiError {
  if (status >= 500) {
    return new ApiError('El servicio no pudo completar la solicitud. Inténtalo nuevamente más tarde.', status)
  }
  if (isRecord(payload) && typeof payload.detail === 'string') {
    return new ApiError(payload.detail, status)
  }
  if (isRecord(payload) && Array.isArray(payload.detail)) {
    const fields: Record<string, string> = {}
    const messages: string[] = []
    for (const item of payload.detail) {
      if (!isRecord(item) || typeof item.msg !== 'string') continue
      messages.push(item.msg)
      if (Array.isArray(item.loc)) {
        const field = item.loc.find((part: unknown) => typeof part === 'string' && part !== 'body' && part !== 'query' && part !== 'path')
        if (typeof field === 'string') fields[field] = item.msg
      }
    }
    return new ApiError(messages.length ? 'Revisa los datos ingresados: ' + messages.join(' · ') : 'Revisa los datos ingresados.', status, fields)
  }
  return new ApiError(`No se pudo completar la solicitud (HTTP ${status}).`, status)
}

type RequestOptions = {
  method?: 'GET' | 'POST'
  body?: unknown
  signal?: AbortSignal
}

export async function request<T>(path: string, decode: (value: unknown) => T, options: RequestOptions = {}): Promise<T> {
  const controller = new AbortController()
  const abort = () => controller.abort(options.signal?.reason)
  if (options.signal?.aborted) abort()
  else options.signal?.addEventListener('abort', abort, { once: true })
  let timedOut = false
  const timeout = globalThis.setTimeout(() => {
    timedOut = true
    controller.abort()
  }, 15000)

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method ?? 'GET',
      headers: {
        Accept: 'application/json',
        ...(options.body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: controller.signal,
    })
    let payload: unknown
    try {
      payload = await response.json()
    } catch {
      if (response.ok) throw new ApiError('El servicio devolvió una respuesta que no se pudo leer.', 502)
      payload = null
    }
    if (!response.ok) throw responseError(response.status, payload)
    return decode(payload)
  } catch (error) {
    if (options.signal?.aborted) throw error
    if (!timedOut && error instanceof ApiError) throw error
    if (options.method === 'POST') {
      throw new ApiError('No pudimos confirmar el registro. Revisa el listado antes de volver a enviarlo.')
    }
    throw new ApiError(timedOut
      ? 'La consulta está tardando demasiado. Inténtalo nuevamente.'
      : 'No se pudo conectar con el servicio. Comprueba tu conexión e inténtalo nuevamente.')
  } finally {
    globalThis.clearTimeout(timeout)
    options.signal?.removeEventListener('abort', abort)
  }
}
