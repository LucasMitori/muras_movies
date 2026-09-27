// Nitro sends no baseline security headers by default, so set them here for
// every response.
//
// Two deliberate omissions:
//
// - CSP. Vuetify's inline styles and Vite's dev-mode HMR both need a
//   carefully scoped policy, and a wrong one fails silently in the browser
//   rather than loudly in CI. It wants its own testing pass.
// - X-Powered-By: Nuxt. Nuxt's SSR renderer sets that header on its way out,
//   after both middleware and the beforeResponse hook have run, so no
//   framework-level hook can remove it (middleware removeResponseHeader,
//   a beforeResponse plugin and a routeRules override were all tried).
//   Strip it at the reverse proxy in front of Nuxt in production.
export default defineEventHandler((event) => {
  setResponseHeader(event, 'X-Content-Type-Options', 'nosniff')
  setResponseHeader(event, 'X-Frame-Options', 'DENY')
  setResponseHeader(event, 'Referrer-Policy', 'strict-origin-when-cross-origin')
  setResponseHeader(event, 'Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
})
