<script setup lang="ts">
const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <VApp>
    <VAppBar flat border="b">
      <VAppBarTitle>
        <NuxtLink to="/" class="text-decoration-none text-high-emphasis"> Muratori </NuxtLink>
      </VAppBarTitle>

      <VSpacer />

      <VBtn to="/" variant="text">Discover</VBtn>

      <template v-if="auth.isAuthenticated">
        <VBtn to="/library" variant="text">My library</VBtn>
        <VBtn variant="text" @click="handleLogout">Log out</VBtn>
      </template>
      <template v-else>
        <VBtn to="/login" variant="text">Log in</VBtn>
        <VBtn to="/register" color="primary" variant="flat" class="ml-2">Sign up</VBtn>
      </template>
    </VAppBar>

    <VMain>
      <VContainer class="py-8">
        <slot />
      </VContainer>
    </VMain>
  </VApp>
</template>
