<script setup lang="ts">
import { ApiError } from '~/composables/useApi'

useHead({ title: 'Log in — Muratori', meta: [{ name: 'robots', content: 'noindex, nofollow' }] })
definePageMeta({ layout: 'default' })

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function submit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Something went wrong. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <VRow justify="center">
    <VCol cols="12" sm="8" md="5" lg="4">
      <VCard>
        <VCardTitle class="text-h5 pt-6">Welcome back</VCardTitle>
        <VCardText>
          <VForm @submit.prevent="submit">
            <VTextField v-model="username" label="Username" autocomplete="username" class="mb-2" />
            <VTextField
              v-model="password"
              label="Password"
              type="password"
              autocomplete="current-password"
              class="mb-2"
            />
            <VAlert v-if="errorMessage" type="error" variant="tonal" density="compact" class="mb-4">
              {{ errorMessage }}
            </VAlert>
            <VBtn type="submit" color="primary" block :loading="loading">Log in</VBtn>
          </VForm>
        </VCardText>
        <VCardActions class="justify-center pb-6">
          <span class="text-body-2">No account yet? <NuxtLink to="/register">Sign up</NuxtLink></span>
        </VCardActions>
      </VCard>
    </VCol>
  </VRow>
</template>
