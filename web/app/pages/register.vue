<script setup lang="ts">
import { ApiError } from '~/composables/useApi'

useHead({ title: 'Sign up — Muratori', meta: [{ name: 'robots', content: 'noindex, nofollow' }] })

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const fieldErrors = ref<Record<string, string[]>>({})

async function submit() {
  loading.value = true
  errorMessage.value = ''
  fieldErrors.value = {}
  try {
    await auth.register(username.value, email.value, password.value)
    router.push('/')
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.message
      fieldErrors.value = error.body?.errors ?? {}
    } else {
      errorMessage.value = 'Something went wrong. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <VRow justify="center">
    <VCol cols="12" sm="8" md="5" lg="4">
      <VCard>
        <VCardTitle class="text-h5 pt-6">Create your account</VCardTitle>
        <VCardText>
          <VForm @submit.prevent="submit">
            <VTextField
              v-model="username"
              label="Username"
              autocomplete="username"
              class="mb-2"
              :error-messages="fieldErrors.username"
            />
            <VTextField
              v-model="email"
              label="Email"
              type="email"
              autocomplete="email"
              class="mb-2"
              :error-messages="fieldErrors.email"
            />
            <VTextField
              v-model="password"
              label="Password"
              type="password"
              autocomplete="new-password"
              class="mb-2"
              hint="At least 10 characters."
              persistent-hint
              :error-messages="fieldErrors.password"
            />
            <VAlert v-if="errorMessage" type="error" variant="tonal" density="compact" class="mt-4 mb-4">
              {{ errorMessage }}
            </VAlert>
            <VBtn type="submit" color="primary" block :loading="loading" class="mt-2">Sign up</VBtn>
          </VForm>
        </VCardText>
        <VCardActions class="justify-center pb-6">
          <span class="text-body-2">Already have an account? <NuxtLink to="/login">Log in</NuxtLink></span>
        </VCardActions>
      </VCard>
    </VCol>
  </VRow>
</template>
