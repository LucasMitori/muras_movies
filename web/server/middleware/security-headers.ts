// Nitro sends no baseline security headers by default (X-Powered-By removal
// lives in server/plugins/strip-powered-by.ts — the SSR renderer sets that
// one after middleware runs, so it needs the beforeResponse hook instead).
// CSP is deliberately left out here — Vuetify's inline styles and Vite's
// dev-mode HMR need a carefully-scoped policy that wants its own testing
// pass rather than a default that might just break the app silently.
export default defineEventHandler((event) => {
  setResponseHeader(event, 'X-Content-Type-Options', 'nosniff')
  setResponseHeader(event, 'X-Frame-Options', 'DENY')
  setResponseHeader(event, 'Referrer-Policy', 'strict-origin-when-cross-origin')
  setResponseHeader(event, 'Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
})
