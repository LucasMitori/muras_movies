import type { ApiErrorBody } from '~/types/api'

const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export class ApiError extends Error {
  status: number
  body: ApiErrorBody | null

  constructor(status: number, body: ApiErrorBody | null) {
    super(body?.detail || `Request failed with status ${status}`)
    this.status = status
    this.body = body
  }
}

/**
 * $fetch instance for talking to the Django API. Always same-origin
 * (/api/...) so the session cookie is sent automatically; mutating
 * requests get Django's CSRF token echoed back from the csrftoken cookie.
 */
export function useApi() {
  const config = useRuntimeConfig()

  return $fetch.create({
    baseURL: config.public.apiBase,
    credentials: 'include',
    onRequest({ options }) {
      options.headers = new Headers(options.headers)

      // SSR runs in Node, so it has no browser cookie jar of its own —
      // forward the incoming request's cookies or the Django session
      // (and thus the logged-in user) would appear logged-out on first render.
      if (import.meta.server) {
        const forwarded = useRequestHeaders(['cookie']).cookie
        if (forwarded) options.headers.set('cookie', forwarded)
      }

      const method = (options.method || 'GET').toString().toUpperCase()
      if (!MUTATING_METHODS.has(method)) return

      const csrfToken = useCookie('csrftoken').value
      if (csrfToken) {
        options.headers.set('X-CSRFToken', csrfToken)
      }
    },
    onResponseError({ response }) {
      throw new ApiError(response.status, response._data as ApiErrorBody | null)
    },
  })
}
