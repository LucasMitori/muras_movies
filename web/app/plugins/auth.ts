export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  // @pinia/nuxt hydrates SSR-fetched state into the client payload, so this
  // only actually hits the network once per navigation, not once per env.
  if (auth.status === 'idle') {
    await auth.fetchCurrentUser()
  }
})
