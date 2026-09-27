// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: true,

  modules: ['@pinia/nuxt', 'vuetify-nuxt-module', '@nuxt/eslint'],

  typescript: {
    strict: true,
    typeCheck: false,
  },

  runtimeConfig: {
    public: {
      // Browser calls always go through same-origin /api (see routeRules
      // below) so session cookies stay same-site even though Nuxt (3000)
      // and Django (8000) run on different ports in dev.
      apiBase: '/api',
    },
  },

  routeRules: {
    '/api/**': { proxy: `${process.env.NUXT_API_BASE || 'http://localhost:8000'}/api/**` },
  },

  vuetify: {
    vuetifyOptions: './app/vuetify.config.ts',
  },
})
