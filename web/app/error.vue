<script setup lang="ts">
defineProps<{ error: { statusCode: number; statusMessage?: string } }>()

useHead({ meta: [{ name: 'robots', content: 'noindex' }] })
</script>

<template>
  <VApp>
    <VMain>
      <VContainer class="py-16 text-center">
        <h1 class="text-h3 mb-2">{{ error.statusCode === 404 ? 'Title not found' : 'Something went wrong' }}</h1>
        <p class="text-body-1 text-medium-emphasis mb-6">
          {{ error.statusMessage || 'Please try again in a moment.' }}
        </p>
        <VBtn color="primary" to="/" @click="clearError({ redirect: '/' })">Back to discovery</VBtn>
      </VContainer>
    </VMain>
  </VApp>
</template>
