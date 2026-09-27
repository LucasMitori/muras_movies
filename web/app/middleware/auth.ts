export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    return navigateTo({ path: '/login', query: { next: to.fullPath } })
  }
})
